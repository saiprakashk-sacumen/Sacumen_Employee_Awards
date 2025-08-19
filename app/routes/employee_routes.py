from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Employee
from typing import List, Dict
from fastapi import Query

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/")
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.get("/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
