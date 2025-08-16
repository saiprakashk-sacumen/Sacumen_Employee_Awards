from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
SECRET_KEY = "your-secret-key"  # store in env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

# ---- Request Models ----
class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "manager"   # default role can be manager (or "user")

class SignUpResponse(BaseModel):
    message: str
    user_id: int
    email: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signin", response_model=AuthResponse)
def signin(payload: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user.email, "role": user.role}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer", "role": user.role}



# ---- Password Utils ----
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ---- Signup Endpoint ----
@router.post("/signup", response_model=SignUpResponse)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_approved=False  # manager onboarding pending until super admin approves
        # created_at and updated_at will be auto-set
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully. Awaiting approval.",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "created_at": new_user.created_at
    }