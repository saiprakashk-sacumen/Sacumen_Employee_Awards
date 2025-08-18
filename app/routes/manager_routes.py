from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db import SessionLocal
from app.models import User, Employee
from pydantic import BaseModel
from datetime import datetime

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


# ---- Pydantic Response Model ----
class ManagerResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_approved: bool
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/{manager_id}", response_model=ManagerResponse)
def get_manager(
    manager_id: int,
    current_user: User = Depends(get_current_user),  # JWT validated here
    db: Session = Depends(get_db)
):
    if current_user.role not in ["superadmin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view manager details"
        )

    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return manager


# ---- List all managers (optionally filter approved) ----
@router.get("/")
def list_managers(
    approved: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only superadmin can list all managers
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list managers"
        )

    query = db.query(User).filter(User.role == "manager")
    if approved is not None:
        query = query.filter(User.is_approved == approved)
    return query.all()

# ---- Approve a manager (super admin only) ----
@router.patch("/{manager_id}/approve")
def approve_manager(
    manager_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can approve managers"
        )

    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    if manager.is_approved:
        return {"message": "Manager is already approved", "manager_id": manager.id}

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

# ---- Get employees of a manager ----flat list of all employees under a manager.
@router.get("/{manager_id}/employees")
def get_manager_employees(
    manager_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only superadmin or the manager themselves can view employees
    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    if current_user.role != "superadmin" and current_user.id != manager_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to view employees of this manager")

    return [employee for employee in manager.employees]  # requires relationship in User model


# ------projects assigned to a manager and their employees grouped by project.
@router.get("/{manager_id}/projects")
def get_manager_projects(manager_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Manager can see only own projects
    if current_user.role == "manager" and current_user.id != manager_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    manager = db.query(User).filter(User.id == manager_id, User.role == "manager").first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    projects = db.query(Employee.project).filter(Employee.manager_id == manager_id).distinct().all()
    project_list = [proj for (proj,) in projects]

    # Optional: include employees under each project
    result: List[Dict] = []
    for proj in project_list:
        employees = db.query(Employee).filter(Employee.manager_id == manager_id, Employee.project == proj).all()
        result.append({
            "project_name": proj,
            "assigned_employees": [{"id": e.id, "name": e.name, "email": e.email} for e in employees]
        })

    return {
        "manager_id": manager_id,
        "manager_name": manager.name,
        "projects": result
    }