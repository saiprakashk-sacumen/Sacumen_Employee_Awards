from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.jira_metrics import fetch_jira_data

router = APIRouter()

@router.get("/metrics")
async def metrics():
    # Update Jira metrics before returning
    fetch_jira_data()
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
