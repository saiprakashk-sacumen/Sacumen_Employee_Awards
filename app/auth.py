from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    username: str
    password: str

@router.post("/signup")
def signup(payload: AuthRequest):
    print("hello world !!")
    return {"message": f"User {payload.username} signed up successfully"}

@router.post("/signin")
def signin(payload: AuthRequest):
    if payload.username != "test" or payload.password != "secret":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
