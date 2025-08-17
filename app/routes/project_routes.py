from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct   # ✅ FIX
from app.db import get_db
from app.models import Employee

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(distinct(Employee.project)).all()
    return [project for (project,) in projects]

@router.get("/{project_name}/employees")
def get_project_employees(project_name: str, db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(Employee.project == project_name).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this project")
    return employees