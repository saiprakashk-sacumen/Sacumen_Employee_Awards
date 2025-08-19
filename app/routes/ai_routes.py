from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import SentimentResult, Employee, User, Nomination
from app.db import get_db

# ----- CONFIG -----
SECRET_KEY = "your-secret-key"          # move to settings/env
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

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


class SentimentResultResponse(BaseModel):
    nomination_id: int
    employee_id: str               # <-- CHANGED to str
    employee_name: Optional[str]
    manager_id: int
    manager_name: Optional[str]
    project_name: Optional[str]
    nomination_type: Optional[str]
    sentiment_label: Optional[str]
    sentiment_score: Optional[float]
    predicted_core_value: Optional[str]
    core_value_alignment: Optional[int]   # <-- CHANGED to int
    analyzed_at: datetime

    class Config:
        orm_mode = True


# ---- Route ----
@router.get("/api/sentiment-results", response_model=List[SentimentResultResponse])
def list_sentiment_results(
    nomination_type: Optional[str] = Query("monthly", description="Filter by nomination type: monthly, quarterly, yearly"),
    search: Optional[str] = Query(None, description="Search by employee name"),
    manager_id: Optional[int] = Query(None, description="Filter by manager (superadmin only)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SentimentResult)

    # Role-based access
    if current_user.role == "manager":
        query = query.filter(SentimentResult.manager_id == current_user.id)
    elif current_user.role == "superadmin":
        if manager_id:
            query = query.filter(SentimentResult.manager_id == manager_id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Default = monthly
    if nomination_type:
        query = query.filter(SentimentResult.nomination_type == nomination_type)

    if nomination_type == "monthly":
        now = datetime.now()
        query = query.filter(
            SentimentResult.analyzed_at >= datetime(now.year, now.month, 1),
            SentimentResult.analyzed_at < datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        )

    # Join with Employee for search
    query = query.join(Employee, SentimentResult.employee_id == Employee.id)

    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))

    sentiment_results = query.all()

    result = []
    for sr in sentiment_results:
        employee = db.query(Employee).filter(Employee.id == sr.employee_id).first()
        manager = db.query(User).filter(User.id == sr.manager_id).first()

        result.append(SentimentResultResponse(
            nomination_id=sr.nomination_id,
            employee_id=sr.employee_id,
            employee_name=employee.name if employee else None,
            manager_id=sr.manager_id,
            manager_name=manager.name if manager else None,
            project_name=sr.project_name,
            nomination_type=sr.nomination_type,
            sentiment_label=sr.sentiment_label,
            sentiment_score=sr.sentiment_score,
            predicted_core_value=sr.predicted_core_value,
            core_value_alignment=sr.core_value_alignment,
            analyzed_at=sr.analyzed_at
        ))

    return result



from sqlalchemy.orm import Session
from sqlalchemy import func

def get_best_employees(manager_id: int, db: Session):
    # Join Nomination + SentimentResult
    results = (
        db.query(
            Employee.id.label("employee_id"),
            Employee.name.label("employee_name"),
            func.avg(Nomination.rating).label("avg_rating"),
            func.avg(SentimentResult.sentiment_score).label("avg_sentiment"),
            func.avg(SentimentResult.core_value_alignment).label("avg_alignment")
        )
        .join(Nomination, Nomination.nominee_id == Employee.id)
        .join(SentimentResult, SentimentResult.nomination_id == Nomination.id)
        .filter(Employee.manager_id == manager_id)
        .group_by(Employee.id)
        .all()
    )

    # Compute weighted score
    scored_employees = []
    for r in results:
        avg_rating = float(r.avg_rating) if r.avg_rating is not None else 0
        avg_sentiment = float(r.avg_sentiment) if r.avg_sentiment is not None else 0
        avg_alignment = float(r.avg_alignment) if r.avg_alignment is not None else 0

        total_score = (avg_rating / 5 * 0.4) + (avg_sentiment * 0.3) + (avg_alignment / 100 * 0.3)

        scored_employees.append({
            "employee_id": r.employee_id,
            "employee_name": r.employee_name,
            "score": total_score
        })


    # Sort by score descending
    scored_employees.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    for i, emp in enumerate(scored_employees, start=1):
        emp["rank"] = i

    return scored_employees


# ---- Route: Best Employees (superadmin only) ----
@router.get("/superadmin/best_employees")
def best_employees_superadmin(
    manager_id: Optional[int] = None,   # filter by specific manager if needed
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only superadmin allowed
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized. Only superadmin can access this.")

    if manager_id is None:
        raise HTTPException(status_code=400, detail="manager_id query param required")

    top_employees = get_best_employees(manager_id, db)
    return {"manager_id": manager_id, "top_employees": top_employees}