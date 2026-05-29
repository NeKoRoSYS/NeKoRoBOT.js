import os
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from db.db_controller import create_user, get_user, update_user, delete_user

router = APIRouter(prefix="/api/users", tags=["Users"])
security = HTTPBearer()

def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_token = os.getenv('APITOKEN')
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid or missing API Token")
    return credentials.credentials

class CreateUserRequest(BaseModel):
    discord_id: str
    username: str

class UpdateUserRequest(BaseModel):
    bio: str

@router.post("/", dependencies=[Depends(verify_api_token)])
async def create_user(request: CreateUserRequest):
    success = await create_user(request.discord_id, request.username)
    if not success:
        raise HTTPException(status_code=409, detail="User already exists")
    return {"message": "User created successfully"}

@router.get("/{discord_id}", dependencies=[Depends(verify_api_token)])
async def get_user(discord_id: str):
    user = await get_user(discord_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{discord_id}", dependencies=[Depends(verify_api_token)])
async def update_user(discord_id: str, request: UpdateUserRequest):
    success = await update_user(discord_id, request.bio)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@router.delete("/{discord_id}", dependencies=[Depends(verify_api_token)])
async def delete_user(discord_id: str):
    success = await delete_user(discord_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}