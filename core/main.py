import json
import asyncio
import logging
import os
import secrets
from dotenv import load_dotenv
from pydantic import ValidationError
from db.db_schemas import BasePayload
from db.repo_factory import db
import logic.db_handler
import websockets
import collections
import time

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

class WebSocketServer:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('APITOKEN')
        self.HEADER = os.getenv('CLIENTHEADER')

        if not self.TOKEN:
            raise ValueError("FATAL ERROR: The 'TOKEN' environment variable is not set or empty in .env file.")

        if not self.HEADER:
            raise ValueError("FATAL ERROR: The 'HEADER' environment variable is not set or empty in .env file.")
    
        self.authenticated_clients = set()
        
        self.ROUTES = {
            'handshake': logic.db_handler.handle_handshake,
            'create_user': logic.db_handler.handle_create,
            'read_user': logic.db_handler.handle_read,
            'update_user': logic.db_handler.handle_update,
            'delete_user': logic.db_handler.handle_delete
        }
        
    async def handle_connection(self, websocket):
        logging.info("New WebSocket connection established.")
        
        logging.info(f"Incoming headers: {websocket.request.headers}")
        
        client_id = websocket.request.headers.get("Client-ID", "")
        auth_header = websocket.request.headers.get("Authorization", "")
        
        if not secrets.compare_digest(client_id, f"{self.HEADER}"):
            logging.warning(f"Blocked connection: Invalid Client ID. Got: '{client_id}'")
            await websocket.close(code=1008, reason="Policy Violation")
            return
            
        if not secrets.compare_digest(auth_header, f"Bearer {self.TOKEN}"):
            logging.warning("Blocked connection: Invalid Authorization header.")
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        try:
            first_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            payload = json.loads(first_message)
            if not isinstance(payload, dict):
                raise ValueError("Handshake payload is not a dictionary")
            data = BasePayload(**payload)
            
            if data.action != 'handshake':
                logging.warning(f"Expected handshake, got: {data.action}")
                await websocket.close(code=1008, reason="Handshake Required First")
                return
                
            success = await logic.db_handler.handle_handshake(websocket, payload, data.interaction_id)
            if success:
                self.authenticated_clients.add(websocket)
                logging.info("Client successfully authenticated.")
            else:
                await websocket.close(code=1008, reason="Unauthorized")
                return

        except asyncio.TimeoutError:
            logging.warning("Connection dropped: Handshake timeout.")
            await websocket.close(code=1008, reason="Handshake Timeout")
            return
        except (json.JSONDecodeError, ValidationError):
            logging.warning("Dropped connection: Malformed handshake payload.")
            await websocket.close(code=1008, reason="Invalid Payload")
            return
        except Exception as e:
            logging.error(f"Handshake error: {e}")
            await websocket.close(code=1011, reason="Internal Error")
            return
        
        limiter = RateLimiter(max_actions=25, timeframe=1)
        try:
            async for message in websocket:
                try:
                    if not limiter.is_allowed():
                        logging.warning("Rate limit exceeded for a client.")
                        await websocket.send(json.dumps({
                            "error": True,
                            "message": "Too many requests. Please slow down.",
                            "interaction_id": None
                        }))
                        continue
                    
                    
                    try:
                        payload = json.loads(message)
                        if not isinstance(payload, dict):
                            raise ValueError("Payload is not a dictionary")
                        data = BasePayload(**payload)
                    except (json.JSONDecodeError, ValidationError, ValueError) as e:
                        logging.error(f"Dropped malformed base payload: {e}")
                        continue
                    
                    action = data.action
                    interaction_id = data.interaction_id

                    if websocket not in self.authenticated_clients:
                        logging.error(f"Blocked unauthenticated command attempt: {action}")
                        await websocket.send(json.dumps({"error": True, "message": "Unauthorized. Handshake required."}))
                        await websocket.close(code=1008, reason="Policy Violation")
                        return
                        
                    handler = self.ROUTES.get(action)
                    if handler:
                        try:
                            await handler(websocket, payload, interaction_id)
                        except Exception as e:
                            logging.error(f"Internal Error in {action}: {e}")
                            await websocket.send(json.dumps({
                                "error": True, 
                                "message": "Internal server error occurred.", 
                                "interaction_id": interaction_id
                            }))
                    else:
                        logging.error(f"Unknown action received: {action}")
        
                except json.JSONDecodeError:
                    logging.error("Received invalid JSON format.")
                    
        except websockets.exceptions.ConnectionClosedOK:
            logging.info("WebSocket connection closed cleanly.")
        except Exception as e:
            logging.exception("An unexpected WebSocket connection error occurred:")
        finally:
            if websocket in self.authenticated_clients:
                self.authenticated_clients.remove(websocket)

    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        print("Initializing database indexes...")
        await db.initialize_all()

        server = websockets.serve(self.handle_connection, host, port, ping_interval=20, ping_timeout=20)
        
        print(f"Python WebSocket server listening on ws://{host}:{port}")
        async with server:
            await asyncio.Future()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    server = WebSocketServer()
    asyncio.run(server.start()) 