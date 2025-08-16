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
