from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.db import get_db
from app.models import Employee, User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

# ---- Router ----
router = APIRouter(prefix="/projects", tags=["Projects"])

# ---- JWT Config ----
SECRET_KEY = "your-secret-key"  # store securely in env variable
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

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

# ---- List all distinct projects ----
@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(distinct(Employee.project)).all()
    return [project for (project,) in projects]

# ---- List employees of a project ----
@router.get("/{project_name}/employees")
def get_project_employees(project_name: str, db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(Employee.project == project_name).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this project")
    return employees

# ---- Assign manager to project (super admin only) ----
@router.patch("/{project_name}/assign_manager/{manager_id}")
def assign_manager_to_project(
    project_name: str,
    manager_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only super admin can assign
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can assign managers to projects"
        )

    # Check manager exists and is approved
    manager = db.query(User).filter(User.id == manager_id, User.role == "manager", User.is_approved == True).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found or not approved")

    # Get employees of project
    employees = db.query(Employee).filter(Employee.project == project_name).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this project")

    # Assign manager to each employee
    for emp in employees:
        emp.manager_id = manager_id

    db.commit()
    return {
        "message": f"Manager '{manager.name}' assigned to project '{project_name}' successfully",
        "manager_id": manager.id,
        "project_name": project_name,
        "assigned_employees": [emp.id for emp in employees]
    }
