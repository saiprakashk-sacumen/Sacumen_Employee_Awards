from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db import SessionLocal
from app.models import User

# ---- Router ----
router = APIRouter(prefix="/managers", tags=["Managers"])

# ---- JWT Config ----
SECRET_KEY = "your-secret-key"  # store securely in env variable
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

# ---- DB Dependency ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Auth Dependency ----
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception
    return user

# ---- List all managers (optionally filter approved) ----
@router.get("/")
def list_managers(approved: bool = None, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.role == "manager")
    if approved is not None:
        query = query.filter(User.is_approved == approved)
    return query.all()

# ---- Approve a manager (super admin only) ----
@router.patch("/{manager_id}/approve")
def approve_manager(manager_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only super admin can approve
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can approve managers"
        )

    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Check if already approved
    if manager.is_approved:
        return {"message": "Manager is already approved", "manager_id": manager.id}

    # Approve manager
    manager.is_approved = True
    db.commit()
    db.refresh(manager)

    return {
        "message": "Manager approved successfully",
        "manager_id": manager.id,
        "name": manager.name,
        "email": manager.email,
        "role": manager.role,
        "is_approved": manager.is_approved
    }
# ---- Get employees of a manager ----
@router.get("/{manager_id}/employees")
def get_manager_employees(manager_id: int, db: Session = Depends(get_db)):
    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return [employee for employee in manager.employees]  # assumes relationship set up in User model
