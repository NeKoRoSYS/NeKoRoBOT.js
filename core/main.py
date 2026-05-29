import os
import time
import uuid
import jwt
import orjson
import asyncio
import logging
import secrets
import collections
from dotenv import load_dotenv
from pydantic import ValidationError
from contextlib import asynccontextmanager
import valkey.asyncio as valkey
from api.websockets import ROUTES
from api.rest import router as rest_router
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from db.db_schemas import BasePayload
from db.db_factory import db
import logic.ws_handler

class RateLimiter:
    def __init__(self, max_actions: int, timeframe: float = 1.0):
        self.max_actions = max_actions
        self.timeframe = timeframe
        self.history = collections.deque()

    def is_allowed(self) -> bool:
        now = time.perf_counter()
        
        while self.history and (now - self.history[0] > self.timeframe):
            self.history.popleft()
            
        if len(self.history) < self.max_actions:
            self.history.append(now)
            return True
            
        return False

class DistributedRateLimiter:
    """Sliding-window rate limiter utilizing a distributed Valkey cluster."""
    def __init__(self, valkey_client: valkey.Valkey, max_actions: int = 25, timeframe: float = 1.0):
        self.vk = valkey_client
        self.max_actions = max_actions
        self.timeframe = timeframe

    async def is_allowed(self, client_id: str) -> bool:
        """Determines if a client is within their allowed action threshold."""
        key = f"rate_limit:{client_id}"
        now = time.time()
        clear_before = now - self.timeframe
        
        async with self.vk.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, clear_before)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, int(self.timeframe) + 2)
            _, current_count, _, _ = await pipe.execute()
            
        return current_count < self.max_actions

class WebSocketServer:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('APITOKEN')
        self.HEADER = os.getenv('CLIENTHEADER')
        self.VALKEYURL = os.getenv('VALKEYURL')
        self.JWTSECRET = os.getenv('JWTSECRET')
        
        self.instance_id = str(uuid.uuid4())
        self.CHANNELNAME = f"ws_instance:{self.instance_id}"

        if not self.TOKEN:
            raise ValueError("FATAL ERROR: The 'TOKEN' environment variable is not set or empty in .env file.")

        if not self.HEADER:
            raise ValueError("FATAL ERROR: The 'HEADER' environment variable is not set or empty in .env file.")
    
        self.app = FastAPI(lifespan=self.lifespan)
        self.app.state.ws_server = self
        self.app.include_router(rest_router)
        self.app.add_api_websocket_route("/ws", self.websocket_endpoint)
        self.ROUTES = ROUTES
        self.local_connections = {}
        self.vk = None
        self.limiter = None
        self.pubsub_task = None
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        logging.info("Initializing database indexes...")
        await db.initialize_all()
        logging.info("Connecting to Valkey...")
        self.vk = valkey.from_url(self.VALKEYURL, decode_responses=True)
        self.limiter = DistributedRateLimiter(self.vk, max_actions=25, timeframe=1.0)
        self.pubsub_task = asyncio.create_task(self._valkey_pubsub_listener())
        yield
        if self.pubsub_task:
            self.pubsub_task.cancel()
            try:
                await self.pubsub_task
            except asyncio.CancelledError:
                pass
        await self.vk.close()
        
    async def _valkey_pubsub_listener(self):
        """Listens ONLY to this specific instance's channel for incoming remote messages."""
        ps = self.vk.pubsub()
        await ps.subscribe(self.CHANNELNAME)
        logging.info(f"Instance {self.instance_id} subscribed to routing bus channel: {self.CHANNELNAME}")
        
        try:
            async for message in ps.listen():
                if message["type"] != "message":
                    continue
                
                try:
                    packet = orjson.loads(message["data"])
                    target_id = packet.get("target_client_id")
                    payload_data = packet.get("data")
                    
                    target_socket = self.local_connections.get(target_id)
                    if target_socket:
                        await target_socket.send_bytes(orjson.dumps(payload_data))
                    else:
                        logging.warning(f"Client {target_id} offline. Pushing to DLQ.")
                        dlq_key = f"dlq:{target_id}"
                        
                        async with self.vk.pipeline(transaction=True) as pipe:
                            pipe.rpush(dlq_key, orjson.dumps(payload_data))
                            pipe.expire(dlq_key, 60)
                            await pipe.execute()
                            
                except Exception as e:
                    logging.error(f"Error distributing message payload over PubSub: {e}")
        except asyncio.CancelledError:
            logging.info("Valkey Pub/Sub listener routine shutdown smoothly.")
        finally:
            await ps.unsubscribe(self.CHANNELNAME)

    async def route_message(self, target_client_id: str, payload_data: dict) -> bool:
        """
        Intelligently routes a message to a client, whether they are connected 
        to this specific server instance or another instance in the cluster.
        """
        if target_client_id in self.local_connections:
            try:
                await self.local_connections[target_client_id].send_bytes(orjson.dumps(payload_data))
                return True
            except Exception as e:
                logging.error(f"Failed to send local message to {target_client_id}: {e}")
                return False

        target_instance_id = await self.vk.get(f"client_route:{target_client_id}")
        
        if target_instance_id:
            packet = {
                "target_client_id": target_client_id,
                "data": payload_data
            }
            await self.vk.publish(f"ws_instance:{target_instance_id}", orjson.dumps(packet))
            return True

        logging.warning(f"Could not route message: Client {target_client_id} is offline or not mapped.")
        return False
        
    async def websocket_endpoint(self, websocket: WebSocket):
        logging.info("New WebSocket connection established.")
        
        await websocket.accept()
        
        auth_header = websocket.headers.get("Authorization", "")
        if not secrets.compare_digest(auth_header, f"Bearer {self.TOKEN}"):
            logging.warning("Blocked connection: Invalid Authorization header.")
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        try:
            first_message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            payload = orjson.loads(first_message)
            
            if not isinstance(payload, dict):
                raise ValueError("Handshake payload is not a dictionary")
            
            data = BasePayload(**payload)
            if data.action != 'handshake':
                logging.warning(f"Expected handshake, got: {data.action}")
                await websocket.close(code=1008, reason="Handshake Required First")
                return
            
            token = payload.get("token")
            if not token:
                await websocket.close(code=1008, reason="JWT Required in Handshake")
                return
            
            try:
                decoded = jwt.decode(token, self.JWTSECRET, algorithms=["HS256"])
                client_id = str(decoded.get("sub"))
                if not client_id:
                    raise ValueError("JWT missing 'sub' claim")
            except jwt.ExpiredSignatureError:
                await websocket.close(code=1008, reason="Token Expired")
                return
            except jwt.InvalidTokenError:
                await websocket.close(code=1008, reason="Invalid Token")
                return
            
            success = await logic.ws_handler.handle_handshake(websocket, payload, data.interaction_id)
            if not success:
                await websocket.close(code=1008, reason="Database Handshake Rejected")
                return

            self.local_connections[client_id] = websocket
            await self.vk.set(f"client_route:{client_id}", self.instance_id)
            logging.info(f"Client {client_id} authenticated and routed to {self.instance_id}.")

            dlq_key = f"dlq:{client_id}"
            while True:
                queued_msg = await self.vk.lpop(dlq_key)
                if not queued_msg:
                    break
                await websocket.send_bytes(queued_msg)
                logging.info(f"Delivered queued DLQ message to {client_id}")
            
        except (asyncio.TimeoutError, orjson.JSONDecodeError, ValidationError, Exception) as e:
            logging.error(f"Handshake failure: {e}")
            await websocket.close(code=1008, reason="Handshake Error")
            return
        
        try:
            while True:
                message = await websocket.receive_text()
                
                if len(message) > 65536:  # 64 KB limit
                    logging.warning(f"Payload from {client_id} exceeded limits.")
                    continue

                if not await self.limiter.is_allowed(client_id):
                    await websocket.send_bytes(orjson.dumps({
                        "error": True, 
                        "message": "Too many requests. Please slow down.", 
                        "interaction_id": None
                    }))
                    continue
                
                try:
                    payload = orjson.loads(message)
                    if not isinstance(payload, dict):
                        raise ValueError("Payload is not a dictionary")
                    data = BasePayload(**payload)
                except (orjson.JSONDecodeError, ValidationError, ValueError) as e:
                    logging.error(f"Dropped malformed base payload: {e}")
                    continue
                
                action = data.action
                interaction_id = data.interaction_id

                if not await self.vk.exists(f"client_route:{client_id}"):
                    await websocket.close(code=1008, reason="Session Invalidated")
                    return
                    
                handler = self.ROUTES.get(action)
                if handler:
                    try:
                        await handler(websocket, payload, interaction_id)
                    except Exception as e:
                        logging.error(f"Internal Error in handler execution logic {action}: {e}")
                        await websocket.send_bytes(orjson.dumps({
                            "error": True, "message": "Internal server error.", "interaction_id": interaction_id
                        }))
                else:
                    logging.error(f"Unknown action: {action}")
        
        except WebSocketDisconnect:
            logging.info("WebSocket connection closed cleanly.")
        except Exception as e:
            logging.exception("An unexpected WebSocket connection error occurred:")
        finally:
            self.local_connections.pop(client_id, None)
            if client_id:
                current_route = await self.vk.get(f"client_route:{client_id}")
                if current_route == self.instance_id:
                    await self.vk.delete(f"client_route:{client_id}")
                
                await self.vk.delete(f"rate_limit:{client_id}")

server = WebSocketServer()
app = server.app

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
        ws_max_size=1048576
    )