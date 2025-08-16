from app.db import SessionLocal
from app.models import User
from passlib.hash import bcrypt

def seed_superadmin():
    db = SessionLocal()
    superadmin_email = "superadmin@sacumen.com"
    
    exists = db.query(User).filter(User.email == superadmin_email).first()
    if exists:
        print("Superadmin already exists.")
    else:
        hashed_password = bcrypt.hash("Admin@123")
        superadmin = User(
            name="Super Admin",
            email=superadmin_email,
            password_hash=hashed_password,
            role="superadmin"
        )
        db.add(superadmin)
        db.commit()
        print("Superadmin created successfully.")
    db.close()
