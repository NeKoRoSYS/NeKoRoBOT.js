import json
import asyncio
import logging
import os
import secrets
from dotenv import load_dotenv
from pydantic import ValidationError
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from db.db_schemas import BasePayload
from db.repo_factory import db
import logic.db_handler
import collections
import time

# Helps prevent spam
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

# The server
class WebSocketServer:
    def __init__(self):
        load_dotenv()
        self.TOKEN = os.getenv('APITOKEN')
        self.HEADER = os.getenv('CLIENTHEADER')

        if not self.TOKEN:
            raise ValueError("FATAL ERROR: The 'TOKEN' environment variable is not set or empty in .env file.")

        if not self.HEADER:
            raise ValueError("FATAL ERROR: The 'HEADER' environment variable is not set or empty in .env file.")
    
        # -- Initialization goes beyond here if the ENV variables are set up correctly
        
        self.authenticated_clients = set()
        
        self.app = FastAPI(lifespan=self.lifespan)
        self.app.add_api_websocket_route("/ws", self.websocket_endpoint)
        
        self.ROUTES = { # Every string of route has a corresponding function found in root/core/logic/db_handler.py
            'handshake': logic.db_handler.handle_handshake,
            'create_user': logic.db_handler.handle_create,
            'read_user': logic.db_handler.handle_read,
            'update_user': logic.db_handler.handle_update,
            'delete_user': logic.db_handler.handle_delete
        }
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        logging.info("Initializing database indexes...")
        await db.initialize_all()
        yield
        
    async def websocket_endpoint(self, websocket: WebSocket):
        logging.info("New WebSocket connection established.")
        
        await websocket.accept()
        
        logging.info(f"Incoming headers: {websocket.headers}")
        
        client_id = websocket.headers.get("Client-ID", "")
        auth_header = websocket.headers.get("Authorization", "")
        
        if not secrets.compare_digest(client_id, f"{self.HEADER}"):
            logging.warning(f"Blocked connection: Invalid Client ID. Got: '{client_id}'")
            await websocket.close(code=1008, reason="Policy Violation")
            return
            
        if not secrets.compare_digest(auth_header, f"Bearer {self.TOKEN}"):
            logging.warning("Blocked connection: Invalid Authorization header.")
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        # -- Connection will only pass if the headers that the Discord.js bot sent matches with the headers set in the ENV variables
        
        try:
            first_message = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            
            # A strict 5-second window where a handshake must be done
            
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

        except asyncio.TimeoutError: # No handshake made in the 5-second window
            logging.warning("Connection dropped: Handshake timeout.")
            await websocket.close(code=1008, reason="Handshake Timeout")
            return
        except (json.JSONDecodeError, ValidationError): # The handshake format isn't correct
            logging.error("Dropped connection: Malformed handshake payload.")
            await websocket.close(code=1008, reason="Invalid Payload")
            return
        except Exception as e: # Something else is wrong
            logging.error(f"Handshake error: {e}")
            await websocket.close(code=1011, reason="Internal Error")
            return
        
        limiter = RateLimiter(max_actions=25, timeframe=1)
        try:
            while True:
                message = await websocket.receive_text()
                
                if not limiter.is_allowed():
                    logging.warning("Rate limit exceeded for a client.")
                    await websocket.send_json({
                        "error": True,
                        "message": "Too many requests. Please slow down.",
                        "interaction_id": None
                    })
                    continue # Tell user to slow down before trying again
                
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

                if websocket not in self.authenticated_clients: # Block unauthorized clients
                    logging.error(f"Blocked unauthenticated command attempt: {action}")
                    await websocket.send_json({"error": True, "message": "Unauthorized. Handshake required."})
                    await websocket.close(code=1008, reason="Policy Violation")
                    return
                    
                handler = self.ROUTES.get(action) # The routes that I discussed earlier on are handled here
                if handler:
                    try:
                        await handler(websocket, payload, interaction_id)
                    except Exception as e:
                        logging.error(f"Internal Error in {action}: {e}")
                        await websocket.send_json({
                            "error": True, 
                            "message": "Internal server error occurred.", 
                            "interaction_id": interaction_id
                        })
                else:
                    logging.error(f"Unknown action received: {action}")

        except WebSocketDisconnect:
            logging.info("WebSocket connection closed cleanly.")
        except Exception as e:
            logging.exception("An unexpected WebSocket connection error occurred:")
        finally:
            if websocket in self.authenticated_clients:
                self.authenticated_clients.remove(websocket)

server = WebSocketServer()
app = server.app

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(
        level=logging.ERROR, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        ws_ping_interval=20.0,
        ws_ping_timeout=20.0,
        ws_max_size=1048576
    )