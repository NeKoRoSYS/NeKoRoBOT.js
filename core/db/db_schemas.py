from pydantic import BaseModel, Field
from typing import Optional

class BasePayload(BaseModel):
    action: str
    interaction_id: str
    
class HandshakePayload(BasePayload):
    bot_id: str
    auth_token: str
    
class DiscordUserPayload(BasePayload):
    discord_id: str

class CreateUserPayload(DiscordUserPayload):
    username: str

class UpdateUserPayload(DiscordUserPayload):
    bio: str