# Employee Awards Backend

This is a **FastAPI** backend service for managing employee awards, including AI sentiment analysis and team/manager management.

---

## Features

- Manage nominations, managers, and employees
- AI-based sentiment analysis for nominations
- Role-based access control (Manager / Superadmin)
- Slack & Jira integration for notifications and tracking
- PostgreSQL for persistent storage
- Prometheus metrics for monitoring
- Dockerized for easy deployment

---

## Technology Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL
- **Monitoring:** Prometheus
- **Integration:** Slack & Jira APIs
- **Containerization:** Docker & Docker Compose

---

## Requirements

- Docker & Docker Compose
- Python 3.11 (for local dev, optional if using Docker)
- PostgreSQL (included in Docker)

---

## Environment Variables

Set the following variables in a `.env` file or via Docker Compose:

```env
DATABASE_URL=postgresql://user:password@db:5432/awards
JWT_SECRET=your_jwt_secret
JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_token
JIRA_DOMAIN=your_jira_domain
PROJECT_KEY=your_project_key
SLACK_TOKEN=your_slack_bot_token

__


Running Locally

1. Stop any running containers
docker compose down

2. Rebuild Docker image from scratch
docker compose build --no-cache


3. Start containers
docker compose up
This will start the API, PostgreSQL and Prometheus 

API Endpoints
Health Check

curl http://localhost:8000/healthz
Manager Endpoints
List Approved Managers (Superadmin only)


GET /managers/approved?approved=true&include_details=true
Query Parameters:

approved (bool, optional) — filter by approved status

include_details (bool, optional) — include team and project details

Example:

curl "http://localhost:8000/managers/approved?approved=true&include_details=true"
Nominations Endpoints
Submit a nomination (Manager only)


POST /nominations
Payload:

{
  "nominee_id": "EMP068",
  "project_name": "Project Alpha",
  "justification_text": "Outstanding contribution",
  "customer_email": "customer@example.com",
  "core_value": "Customer delight",
  "rating": 5,
  "nomination_type": "monthly"
}
List nominations


GET /nominations?nomination_type=monthly&search=John
Query Parameters:

nomination_type (monthly, quarterly, yearly)

search — filter by employee name

manager_id (superadmin only) — filter by manager

Sentiment Results
List sentiment results

GET /api/sentiment-results?nomination_type=monthly&search=John
Query Parameters:

nomination_type (monthly, quarterly, yearly)

search — employee name

manager_id (superadmin only)

Prometheus Metrics
Metrics are exposed at:


GET /metrics
Metrics include:

Nominations submitted per type (monthly, quarterly, yearly)

AI sentiment analysis scores

Employee and manager statistics

Jira ticket counts and logged hours

Slack integration notifications status

These metrics can be scraped directly by Prometheus and visualized in Grafana.

Slack & Jira Integration
Slack: Notifications are sent to configured Slack channels for new nominations and approvals. The Slack token is required in .env.

Jira: Tickets and work logs are integrated with Jira using the Jira API. This allows tracking of employee nominations in Jira boards. Required variables are JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DOMAIN, and PROJECT_KEY.

Database Migrations
We use Alembic for database migrations.

Create a new migration:


alembic revision --autogenerate -m "Your message"
Upgrade to the latest version:


alembic upgrade head
If migrations are out of sync, stamp the database:


alembic stamp head
Notes
Employee IDs are strings (EMPxxx)

Nomination types are enums: monthly, quarterly, yearly

Only managers can submit nominations

Only superadmin can view all managers or filter by manager

Sentiment results are stored per nomination and updated automatically

