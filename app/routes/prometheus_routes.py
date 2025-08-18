from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response

router = APIRouter()

# ---------- Slack ----------
slack_hours = Gauge("slack_hours_total", "Total hours spent in Slack", ["employee_id", "cycle"])
slack_mentions = Counter("slack_mentions_total", "Number of times employee mentioned in Slack", ["employee_id", "cycle"])

# ---------- Jira ----------
jira_hours = Gauge("jira_hours_total", "Total hours spent on Jira tickets", ["employee_id", "cycle"])
jira_tickets = Counter("jira_tickets_total", "Total Jira tickets worked", ["employee_id", "cycle"])

# ---------- Sacufit ----------
sacufit_bmi = Gauge("sacufit_bmi", "Employee BMI score", ["employee_id", "cycle"])
sacufit_prize = Gauge("sacufit_prize", "Prize money from Sacufit activities", ["employee_id", "cycle"])

# ---------- Interview Panel ----------
interview_panel = Counter("interview_panel_total", "Number of interviews helped by employee", ["employee_id", "cycle"])

# ---------- Extracurricular ----------
courses_completed = Counter("extracurricular_courses_total", "Number of courses completed", ["employee_id", "cycle"])
hackathons_participated = Counter("extracurricular_hackathons_total", "Number of hackathons participated", ["employee_id", "cycle"])

# ---------- Sacumen Support ----------
annual_day_participation = Counter("annual_day_participation_total", "Participation in annual day events", ["employee_id", "event_type"])
client_meeting_abroad = Counter("client_meeting_abroad_total", "Abroad client meetings attended", ["employee_id"])

# ---------- Metrics endpoint ----------
@router.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
