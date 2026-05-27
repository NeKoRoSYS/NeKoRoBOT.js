import json
import asyncio
import websockets
import os
from dotenv import load_dotenv
from db.repo_factory import db
import logic.db_handler
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

ROUTES = {
    'handshake': logic.db_handler.handle_handshake,
    'create_user': logic.db_handler.handle_create,
    'read_user': logic.db_handler.handle_read,
    'update_user': logic.db_handler.handle_update,
    'delete_user': logic.db_handler.handle_delete
}

load_dotenv()
TOKEN = os.getenv('APITOKEN')

authenticated_clients = set()

async def handle_connection(websocket):
    print("New WebSocket connection established.")
    
    print(f"Incoming headers: {websocket.request.headers}")
    
    client_id = websocket.request.headers.get("Client-ID", "")
    auth_header = websocket.request.headers.get("Authorization", "")
    
    if client_id != "NexsplitBot/1.0":
        print(f"Blocked connection: Invalid Client ID. Got: '{client_id}'")
        await websocket.close(code=1008, reason="Policy Violation")
        return
        
    if auth_header != f"Bearer {TOKEN}":
        print("Blocked connection: Invalid Authorization header.")
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    limiter = RateLimiter(max_actions=25, timeframe=1)
    try:
        async for message in websocket:
            try:
                if not limiter.is_allowed():
                    print("Rate limit exceeded for a client.")
                    await websocket.send(json.dumps({
                        "error": True,
                        "message": "Too many requests. Please slow down.",
                        "interaction_id": interaction_id
                    }))
                    break
                
                payload = json.loads(message)
                action = payload.get('action')
                interaction_id = payload.get('interaction_id')
                
                if action == 'handshake':
                    success = await logic.db_handler.handle_handshake(websocket, payload, interaction_id)
                    if success:
                        authenticated_clients.add(websocket)
                    else:
                        await websocket.close(code=1008, reason="Unauthorized")
                        return
                    continue

                if websocket not in authenticated_clients:
                    print(f"Blocked unauthenticated command attempt: {action}")
                    await websocket.send(json.dumps({"error": True, "message": "Unauthorized. Handshake required."}))
                    await websocket.close(code=1008, reason="Policy Violation")
                    return
                    
                handler = ROUTES.get(action)
                if handler:
                    try:
                        await handler(websocket, payload, interaction_id)
                    except Exception as e:
                        print(f"Internal Error in {action}: {e}")
                        await websocket.send(json.dumps({
                            "error": True, 
                            "message": "Internal server error occurred.", 
                            "interaction_id": interaction_id
                        }))
                else:
                    print(f"Unknown action received: {action}")
    
            except json.JSONDecodeError:
                print("Received invalid JSON format.")
                
    except websockets.exceptions.ConnectionClosedOK:
        print("WebSocket connection closed cleanly.")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        if websocket in authenticated_clients:
            authenticated_clients.remove(websocket)

async def main():
    print("Initializing database indexes...")
    await db.initialize_all()

    start_server = websockets.serve(handle_connection, "0.0.0.0", 8000, ping_interval=20, ping_timeout=20)

    print("Python WebSocket server listening on ws://0.0.0.0:8000")
    async with start_server:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
