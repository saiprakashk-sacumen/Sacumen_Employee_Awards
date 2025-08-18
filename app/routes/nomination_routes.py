from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User, Employee, Nomination
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.routes.manager_routes import get_current_user 
from fastapi import Query
from app.models import NominationTypeEnum


router = APIRouter(prefix="/nominations", tags=["Nominations"])


from enum import Enum

class NominationCreate(BaseModel):
    nominee_id: str
    project_name: str
    justification_text: str
    customer_email: Optional[str]
    core_value: str
    rating: Optional[int]
    nomination_type: NominationTypeEnum  # ✅ updated

class NominationResponse(BaseModel):
    id: int
    nominee_id: str
    nominee_name: str
    project_name: str
    justification_text: str
    customer_email: Optional[str]
    core_value: str
    rating: Optional[int]
    nomination_type: NominationTypeEnum  # ✅ updated
    manager_id: int
    manager_name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

# ---- POST nomination (create or update) ----
@router.post("/", response_model=NominationResponse)
def submit_nomination(payload: NominationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can submit nominations")

    # Ensure nominee belongs to manager
    employee = db.query(Employee).filter(Employee.id == payload.nominee_id, Employee.manager_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Nominee is not in your team")

    # Determine nomination_type
    nomination_type = payload.nomination_type or NominationTypeEnum.monthly

    # Check if nomination already exists for this employee
    nomination = db.query(Nomination).filter(Nomination.nominee_id == payload.nominee_id, Nomination.manager_id == current_user.id).first()

    if nomination:
        # Update existing
        nomination.justification_text = payload.justification_text
        nomination.customer_email = payload.customer_email
        nomination.core_value = payload.core_value
        nomination.rating = payload.rating
        nomination.project_name = payload.project_name
        nomination.nomination_type = nomination_type
    else:
        # Create new
        nomination = Nomination(
            nominee_id=payload.nominee_id,
            manager_id=current_user.id,
            project_name=payload.project_name,
            justification_text=payload.justification_text,
            customer_email=payload.customer_email,
            core_value=payload.core_value,
            rating=payload.rating,
            nomination_type=nomination_type  # ✅ assign it here
        )

    db.add(nomination)
    db.commit()
    db.refresh(nomination)

    return NominationResponse(
    id=nomination.id,
    nominee_id=employee.id,
    nominee_name=employee.name,
    project_name=nomination.project_name,
    justification_text=nomination.justification_text,
    customer_email=nomination.customer_email,
    core_value=nomination.core_value,
    rating=nomination.rating,
    nomination_type=nomination.nomination_type,  # ✅ assign from DB object
    manager_id=current_user.id,
    manager_name=current_user.name,
    created_at=nomination.created_at,
    updated_at=nomination.updated_at
)


# ---- GET nominations visible to user ----
@router.get("/", response_model=List[NominationResponse])
def list_nominations(
    nomination_type: Optional[str] = Query(None, description="Filter by nomination type: monthly, quarterly, yearly"),
    search: Optional[str] = Query(None, description="Search by employee first name"),
    manager_id: Optional[int] = Query(None, description="Filter by manager, superadmin only"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Base query
    query = db.query(Nomination)

    if current_user.role == "manager":
        # Managers can only see their team's nominations
        query = query.filter(Nomination.manager_id == current_user.id)
    elif current_user.role == "superadmin":
        # Superadmin can optionally filter by manager
        if manager_id:
            query = query.filter(Nomination.manager_id == manager_id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Filter by nomination type if provided
    if nomination_type:
        query = query.filter(Nomination.nomination_type == nomination_type)

    # Join with Employee to allow search by first name
    query = query.join(Employee, Nomination.nominee_id == Employee.id)

    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))

    nominations = query.all()

    result = []
    for nom in nominations:
        employee = db.query(Employee).filter(Employee.id == nom.nominee_id).first()
        manager = db.query(User).filter(User.id == nom.manager_id).first()

        result.append(NominationResponse(
            id=nom.id,
            nominee_id=employee.id,
            nominee_name=employee.name,
            project_name=nom.project_name,
            justification_text=nom.justification_text,
            customer_email=nom.customer_email,
            core_value=nom.core_value,
            rating=nom.rating,
            nomination_type=nom.nomination_type,
            manager_id=manager.id,
            manager_name=manager.name,
            created_at=nom.created_at,
            updated_at=nom.updated_at
        ))

    return result



