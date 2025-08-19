import os
import requests
from prometheus_client import Gauge

# ---- JIRA Prometheus metrics ----
jira_tickets_completed = Gauge("jira_tickets_completed_total", "Total number of completed tickets")
jira_hours_logged = Gauge("jira_hours_logged_total", "Total hours logged in Jira")
jira_avg_hours_per_ticket = Gauge("jira_avg_hours_per_ticket", "Average hours logged per ticket")
jira_open_tickets = Gauge("jira_open_tickets_total", "Total number of open tickets")
jira_tickets_by_status = Gauge("jira_tickets_by_status", "Number of Jira tickets by status", ["status"])
jira_tickets_by_assignee = Gauge("jira_tickets_by_assignee", "Number of Jira tickets per assignee", ["assignee"])


# ---- Jira config from environment variables ----
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "your-domain.atlassian.net")
PROJECT_KEY = os.getenv("PROJECT_KEY", "SCRUM")



JIRA_SEARCH_URL = f"https://{JIRA_DOMAIN}/rest/api/3/search?jql=project={PROJECT_KEY}&fields=status,worklog"



print("Jira email:", JIRA_EMAIL)
print("Jira token set?", bool(JIRA_API_TOKEN))

def fetch_jira_data():
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
        status_counts = {}
        assignee_counts = {}

        issues = data.get("issues", [])
        for issue in issues:
            fields = issue["fields"]
            status = fields["status"]["name"]
            status_counts[status] = status_counts.get(status, 0) + 1

            assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1

            if status.lower() == "done":
                completed += 1

            worklogs = fields.get("worklog", {}).get("worklogs", [])
            ticket_hours = sum([w.get("timeSpentSeconds", 0) / 3600 for w in worklogs])
            total_hours += ticket_hours

        # Update Prometheus metrics
        jira_tickets_completed.set(completed)
        jira_hours_logged.set(total_hours)
        jira_avg_hours_per_ticket.set(total_hours / len(issues) if issues else 0)
        jira_open_tickets.set(status_counts.get("To Do", 0) + status_counts.get("In Progress", 0))

        for s, count in status_counts.items():
            jira_tickets_by_status.labels(status=s).set(count)
        for a, count in assignee_counts.items():
            jira_tickets_by_assignee.labels(assignee=a).set(count)

    except Exception as e:
        print("Error fetching Jira data:", e)



def start_metrics_loop(interval_seconds=30, port=8000):
    """Start Prometheus server and fetch metrics continuously"""
    from prometheus_client import start_http_server
    start_http_server(port)
    print(f"Prometheus metrics available at http://localhost:{port}/metrics")

    def loop():
        while True:
            fetch_jira_data()
            import time; time.sleep(interval_seconds)

    import threading
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()



