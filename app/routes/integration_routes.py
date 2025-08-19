from fastapi import APIRouter
from app.services.slack_service import get_all_users, get_user_activity
from app.services.jira_service import get_users, get_issue_times

router = APIRouter(prefix="/integration", tags=["Integration"])

@router.get("/slack")
def slack_data():
    users = get_all_users()
    data = {name: get_user_activity(uid) for uid, name in users.items()}
    return data

@router.get("/jira/{issue_key}")
def jira_data(issue_key: str):
    user_id, minutes = get_issue_times(issue_key)
    return {"user_id": user_id, "time_spent_minutes": minutes}
