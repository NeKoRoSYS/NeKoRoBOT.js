import os
from db.db_schemas import CreateUserPayload, DiscordUserPayload, HandshakePayload, UpdateUserPayload
from pydantic import ValidationError
from dotenv import load_dotenv
from db.repo_factory import db
from pymongo.errors import DuplicateKeyError

# -- bot --

load_dotenv()
TOKEN = os.getenv('APITOKEN')

in_flight_requests = set()

if not TOKEN:
    raise ValueError("FATAL ERROR: 'TOKEN' is missing in .env file.")

async def handle_handshake(websocket, payload, interaction_id):
    try:
        data = HandshakePayload(**payload)
    except ValidationError as e:
        await websocket.send_json({
            "interaction_id": interaction_id, 
            "error": True, 
            "message": f"Invalid payload format: {e.errors()[0]['msg']}"
        })
        return
    
    bot_id = data.bot_id
    auth_token = data.auth_token
    
    if auth_token != TOKEN:
        print(f"Blocked unauthorized handshake attempt from bot ID: {bot_id}")
        await websocket.send_json({
            "error": True, 
            "message": "Unauthorized: Invalid API Token."
        })
        return False

    print(f"Handshake successful with bot: {bot_id}")
    return True

async def handle_create(websocket, payload, interaction_id):
    try:
        data = CreateUserPayload(**payload)
    except ValidationError as e:
        await websocket.send_json({
            "interaction_id": interaction_id, 
            "error": True, 
            "message": f"Invalid payload format: {e.errors()[0]['msg']}"
        })
        return
    discord_id = data.discord_id
    username = data.username
    
    if discord_id in in_flight_requests:
        return
        
    in_flight_requests.add(discord_id)
    try: # You might have to remove in_flight_requests in the future if you want horizontal scaling
        success = await db.user_repo.create_user(discord_id, username)
        if success:
            await websocket.send_json({"event": "created", "interaction_id": interaction_id})
        else:
            await websocket.send_json({"error": True, "interaction_id": interaction_id, "message": "User already exists!"})
        pass
    finally:
        in_flight_requests.remove(discord_id)

async def handle_read(websocket, payload, interaction_id):
    try:
        data = DiscordUserPayload(**payload)
    except ValidationError as e:
        await websocket.send_json({
            "interaction_id": interaction_id, 
            "error": True, 
            "message": f"Invalid payload format: {e.errors()[0]['msg']}"
        })
        return
    user = await db.user_repo.get_user(data.discord_id)
    if user:
        await websocket.send_json({"event": "read", "interaction_id": interaction_id, "data": user})
    else:
        await websocket.send_json({"error": True, "interaction_id": interaction_id, "message": "User not found."})

async def handle_update(websocket, payload, interaction_id):
    try:
        data = UpdateUserPayload(**payload)
    except ValidationError as e:
        await websocket.send_json({
            "interaction_id": interaction_id, 
            "error": True, 
            "message": f"Invalid payload format: {e.errors()[0]['msg']}"
        })
        return
    success = await db.user_repo.update_bio(data.discord_id, data.bio)
    if success:
        await websocket.send_json({"event": "updated", "interaction_id": interaction_id})
    else:
        await websocket.send_json({"error": True, "interaction_id": interaction_id, "message": "User not found or bio unchanged."})

async def handle_delete(websocket, payload, interaction_id):
    try:
        data = DiscordUserPayload(**payload)
    except ValidationError as e:
        await websocket.send_json({
            "interaction_id": interaction_id, 
            "error": True, 
            "message": f"Invalid payload format: {e.errors()[0]['msg']}"
        })
        return
    success = await db.user_repo.delete_user(data.discord_id)
    if success:
        await websocket.send_json({"event": "deleted", "interaction_id": interaction_id})
    else:
        await websocket.send_json({"error": True, "interaction_id": interaction_id, "message": "User not found."})