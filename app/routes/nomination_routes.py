from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db import get_db
from app.models import Nomination
from pydantic import BaseModel

router = APIRouter(prefix="/nominations", tags=["Nominations"])

# ---- Pydantic Schemas ----
class NominationBase(BaseModel):
    project_name: str
    nominee_id: int
    manager_id: int
    verbiage: str
    core_value: str

class NominationCreate(NominationBase):
    pass

class NominationUpdate(BaseModel):
    project_name: Optional[str] = None
    nominee_id: Optional[int] = None
    manager_id: Optional[int] = None
    verbiage: Optional[str] = None
    core_value: Optional[str] = None

class NominationResponse(NominationBase):
    id: int

    class Config:
        orm_mode = True


# ---- Routes ----
@router.post("/", response_model=NominationResponse)
def create_nomination(nomination: NominationCreate, db: Session = Depends(get_db)):
    new_nomination = Nomination(**nomination.dict())
    db.add(new_nomination)
    db.commit()
    db.refresh(new_nomination)
    return new_nomination


@router.get("/", response_model=List[NominationResponse])
def list_nominations(
    project: Optional[str] = None,
    manager_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Nomination)
    if project:
        query = query.filter(Nomination.project_name == project)
    if manager_id:
        query = query.filter(Nomination.manager_id == manager_id)
    if employee_id:
        query = query.filter(Nomination.nominee_id == employee_id)
    return query.all()


@router.get("/{nomination_id}", response_model=NominationResponse)
def get_nomination(nomination_id: int, db: Session = Depends(get_db)):
    nomination = db.query(Nomination).filter(Nomination.id == nomination_id).first()
    if not nomination:
        raise HTTPException(status_code=404, detail="Nomination not found")
    return nomination


@router.patch("/{nomination_id}", response_model=NominationResponse)
def update_nomination_partial(nomination_id: int, updates: NominationUpdate, db: Session = Depends(get_db)):
    nomination = db.query(Nomination).filter(Nomination.id == nomination_id).first()
    if not nomination:
        raise HTTPException(status_code=404, detail="Nomination not found")

    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(nomination, key, value)

    db.commit()
    db.refresh(nomination)
    return nomination


@router.put("/{nomination_id}", response_model=NominationResponse)
def update_nomination_full(nomination_id: int, new_data: NominationCreate, db: Session = Depends(get_db)):
    nomination = db.query(Nomination).filter(Nomination.id == nomination_id).first()
    if not nomination:
        raise HTTPException(status_code=404, detail="Nomination not found")

    for key, value in new_data.dict().items():
        setattr(nomination, key, value)

    db.commit()
    db.refresh(nomination)
    return nomination
