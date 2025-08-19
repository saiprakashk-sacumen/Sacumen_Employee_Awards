import os
import requests
from prometheus_client import Gauge

# ---- Prometheus metrics ----
tickets_completed = Gauge("jira_tickets_completed_total", "Total number of completed tickets")
hours_logged = Gauge("jira_hours_logged_total", "Total hours logged in Jira")

# ---- Jira config from environment variables ----
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "your-domain.atlassian.net")
PROJECT_KEY = os.getenv("PROJECT_KEY", "SCRUM")

JIRA_SEARCH_URL = f"https://{JIRA_DOMAIN}/rest/api/3/search?jql=project={PROJECT_KEY}&fields=status,worklog"

def fetch_jira_data():
    """Fetch Jira issues and update Prometheus metrics"""
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("Jira credentials not set!")
        return

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(JIRA_SEARCH_URL, headers=headers, auth=auth, timeout=10)
        response.raise_for_status()
        data = response.json()

        completed = 0
        total_hours = 0.0

        for issue in data.get("issues", []):
            fields = issue["fields"]
            status = fields["status"]["name"]
            if status.lower() == "done":
                completed += 1

            worklogs = fields.get("worklog", {}).get("worklogs", [])
            for w in worklogs:
                time_spent_sec = w.get("timeSpentSeconds", 0)
                total_hours += time_spent_sec / 3600

        # Update Prometheus metrics
        tickets_completed.set(completed)
        hours_logged.set(total_hours)

    except Exception as e:
        print("Error fetching Jira data:", e)
