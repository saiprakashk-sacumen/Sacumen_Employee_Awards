from . import auth, models
from .db import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import User, RoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Insert super admin if not exists
    db: Session = SessionLocal()
    try:
        super_admin_email = "hr@sacumen.com"
        existing = db.query(User).filter(User.email == super_admin_email).first()
        if not existing:
            new_admin = User(
                name="Super Admin",
                email=super_admin_email,
                password_hash=pwd_context.hash("supersecret"),
                role=RoleEnum.super_admin
            )
            db.add(new_admin)
            db.commit()
            print("✅ Super admin created.")
        else:
            print("ℹ️ Super admin already exists.")
    finally:
        db.close()

app = FastAPI()

# Initialize DB & insert super admin
init_db()

# Include routes
app.include_router(auth.router)




# from fastapi import FastAPI
# from app import auth  # import auth.py

# app = FastAPI(title="Auth Service")

# # Include auth router
# app.include_router(auth.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
