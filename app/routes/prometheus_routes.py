from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.jira_metrics import fetch_jira_data
from app.slack_metrics import get_all_users, get_user_activity

router = APIRouter()

@router.get("/metrics")
async def metrics():
    # JIRA metrics
    fetch_jira_data()
    
    # Slack metrics
    users = get_all_users()
    for uid in users:
        get_user_activity(uid)
    
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)