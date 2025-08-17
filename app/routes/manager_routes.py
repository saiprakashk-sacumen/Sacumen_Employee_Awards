from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from app.db import get_db
from app.models import User
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/managers", tags=["Managers"])

class ManagerCreate(BaseModel):
    name: str
    email: str
    project: str
    team_member_ids: List[str]

@router.post("/")
def onboard_manager(manager: ManagerCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == manager.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Manager already exists")

    new_manager = User(
        id=str(uuid4()),
        name=manager.name,
        email=manager.email,
        role="MANAGER",
        project=manager.project,
        team_member_ids=",".join(manager.team_member_ids)
    )
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return {"id": new_manager.id, "message": "Manager onboarded successfully"}

@router.get("/")
def list_managers(db: Session = Depends(get_db)):
    managers = db.query(User).filter(User.role == "MANAGER").all()
    return managers
