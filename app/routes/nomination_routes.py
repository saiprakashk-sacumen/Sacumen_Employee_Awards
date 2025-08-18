
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
from app.ai.sentiment import analyze_nomination
from app.models import SentimentResult
from datetime import datetime
from fastapi import Query


router = APIRouter(prefix="/nominations", tags=["Nominations"])


from enum import Enum

class NominationCreate(BaseModel):
    nominee_id: str
    project_name: str
    justification_text: str
    customer_email: Optional[str]
    core_value: str
    rating: Optional[int]
    nomination_type: NominationTypeEnum  # updated

class NominationResponse(BaseModel):
    id: int
    nominee_id: str
    nominee_name: str
    project_name: str
    justification_text: str
    customer_email: Optional[str]
    core_value: str
    rating: Optional[int]
    nomination_type: NominationTypeEnum  # updated
    manager_id: int
    manager_name: str
    created_at: datetime
    updated_at: Optional[datetime]


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
# ---- POST nomination (create or update) ----
@router.post("/", response_model=NominationResponse)
def submit_nomination(
    payload: NominationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can submit nominations")

    # Ensure nominee belongs to manager
    employee = (
        db.query(Employee)
        .filter(Employee.id == payload.nominee_id, Employee.manager_id == current_user.id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=400, detail="Nominee is not in your team")

    # Default nomination_type to monthly at the Pydantic layer OR here:
    nomination_type = payload.nomination_type or NominationTypeEnum.monthly

    # Create or update nomination (1 per employee per manager)
    nomination = (
        db.query(Nomination)
        .filter(Nomination.nominee_id == payload.nominee_id, Nomination.manager_id == current_user.id)
        .first()
    )

    if nomination:
        nomination.project_name = payload.project_name
        nomination.justification_text = payload.justification_text
        nomination.customer_email = payload.customer_email
        nomination.core_value = payload.core_value
        nomination.rating = payload.rating
        nomination.nomination_type = nomination_type
    else:
        nomination = Nomination(
            nominee_id=payload.nominee_id,
            manager_id=current_user.id,
            project_name=payload.project_name,
            justification_text=payload.justification_text,
            customer_email=payload.customer_email,
            core_value=payload.core_value,
            rating=payload.rating,
            nomination_type=nomination_type,
        )
        db.add(nomination)

    db.commit()
    db.refresh(nomination)

    # --- AI sentiment analysis (safe defaults if fields missing) ---
    ai_input = {
        "nomination_id": nomination.id,
        "employee_id": employee.id,            # str
        "manager_id": current_user.id,
        "core_value_claimed": nomination.core_value,
        "comment": nomination.justification_text,
    }
    ai_result = analyze_nomination(ai_input) or {}

    sentiment_label = ai_result.get("sentiment_label", None)
    sentiment_score = ai_result.get("sentiment_score", None)
    predicted_core_value = ai_result.get("predicted_core_value", None)
    alignment = ai_result.get("core_value_alignment", None)

    # Upsert SentimentResult (PK = nomination_id)
    existing = db.query(SentimentResult).filter(SentimentResult.nomination_id == nomination.id).first()
    if existing:
        existing.employee_id = employee.id           # str
        existing.manager_id = current_user.id
        existing.employee_name = employee.name
        existing.manager_name = current_user.name
        existing.project_name = nomination.project_name
        # Enum -> string for SentimentResult
        existing.nomination_type = (
            nomination.nomination_type.value
            if isinstance(nomination.nomination_type, NominationTypeEnum)
            else str(nomination.nomination_type)
        )
        existing.sentiment_label = sentiment_label
        existing.sentiment_score = sentiment_score
        existing.predicted_core_value = predicted_core_value
        existing.core_value_alignment = alignment
        existing.analyzed_at = datetime.utcnow()
    else:
        sr = SentimentResult(
            nomination_id=nomination.id,
            employee_id=employee.id,              # str
            manager_id=current_user.id,
            employee_name=employee.name,
            manager_name=current_user.name,
            project_name=nomination.project_name,
            nomination_type=(
                nomination.nomination_type.value
                if isinstance(nomination.nomination_type, NominationTypeEnum)
                else str(nomination.nomination_type)
            ),
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            predicted_core_value=predicted_core_value,
            core_value_alignment=alignment,
            analyzed_at=datetime.utcnow(),
        )
        db.add(sr)

    db.commit()

    return NominationResponse(
        id=nomination.id,
        nominee_id=employee.id,          # str
        nominee_name=employee.name,
        project_name=nomination.project_name,
        justification_text=nomination.justification_text,
        customer_email=nomination.customer_email,
        core_value=nomination.core_value,
        rating=nomination.rating,
        nomination_type=nomination.nomination_type,
        manager_id=current_user.id,
        manager_name=current_user.name,
        created_at=nomination.created_at,
        updated_at=nomination.updated_at,
    )



# ---- GET nominations visible to user ----
@router.get("/", response_model=List[NominationResponse])
def list_nominations(
    nomination_type: Optional[str] = Query("monthly", description="Filter by nomination type: monthly, quarterly, yearly"),
    search: Optional[str] = Query(None, description="Search by employee first name"),
    manager_id: Optional[int] = Query(None, description="Filter by manager, superadmin only"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Nomination)

    if current_user.role == "manager":
        query = query.filter(Nomination.manager_id == current_user.id)
    elif current_user.role == "superadmin" and manager_id:
        query = query.filter(Nomination.manager_id == manager_id)
    else:
        if current_user.role not in ("manager", "superadmin"):
            raise HTTPException(status_code=403, detail="Not authorized")

    # Validate and apply enum filter
    enum_val = None
    if nomination_type:
        try:
            enum_val = NominationTypeEnum(nomination_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid nomination_type")
        query = query.filter(Nomination.nomination_type == enum_val)

    # Monthly window (current month only)
    if enum_val == NominationTypeEnum.monthly:
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        month_end = (
            datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        )
        query = query.filter(Nomination.created_at >= month_start, Nomination.created_at < month_end)

    # Name search (join)
    query = query.join(Employee, Nomination.nominee_id == Employee.id)
    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))

    rows = query.all()

    out: List[NominationResponse] = []
    for n in rows:
        emp = db.query(Employee).filter(Employee.id == n.nominee_id).first()
        mgr = db.query(User).filter(User.id == n.manager_id).first()
        out.append(
            NominationResponse(
                id=n.id,
                nominee_id=emp.id if emp else n.nominee_id,
                nominee_name=emp.name if emp else "",
                project_name=n.project_name,
                justification_text=n.justification_text,
                customer_email=n.customer_email,
                core_value=n.core_value,
                rating=n.rating,
                nomination_type=n.nomination_type,
                manager_id=mgr.id if mgr else n.manager_id,
                manager_name=mgr.name if mgr else "",
                created_at=n.created_at,
                updated_at=n.updated_at,
            )
        )
    return out
