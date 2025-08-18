<<<<<<< HEAD
from fastapi import APIRouter
from app.ai.sentiment import analyze_nomination
from app.ai.bias import detect_bias
import pandas as pd
from pydantic import BaseModel

router = APIRouter()



class SentimentRequest(BaseModel):
    comment: str
    selected_value: str

@router.post("/api/ai/sentiment")
def sentiment_api(req: SentimentRequest):
    nomination = {
        "nomination_id": 0,
        "employee_id": 0,
        "manager_id": 0,
        "core_value_claimed": req.selected_value,
        "comment": req.comment
    }
    return analyze_nomination(nomination)
=======
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import SentimentResult, Employee, User
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
>>>>>>> origin/dev
