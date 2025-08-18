import logging
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

# -------------------------------------------------
# Logging Setup
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(title="Employee Awards Backend")

# -------------------------------------------------
# Data Models
# -------------------------------------------------
class Manager(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    project: str
    team_member_ids: List[str]

class Employee(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    department: str

class Nomination(BaseModel):
    id: Optional[str] = None
    project_name: str
    justification_text: str
    customer_email: str
    core_value: str
    rating: int
    nominee_id: str
    created_at: Optional[str] = None
    status: str = "PENDING"
    is_winner: bool = False

# -------------------------------------------------
# In-Memory Storage
# -------------------------------------------------
managers: List[Manager] = []
employees: List[Employee] = []
nominations: List[Nomination] = []

# -------------------------------------------------
# Manager Onboarding
# -------------------------------------------------
@app.post("/managers")
def create_manager(manager: Manager):
    try:
        manager.id = str(uuid4())
        managers.append(manager)
        logger.info(f"Manager onboarded: {manager.name}")
        return {"id": manager.id, "message": "Manager onboarded successfully"}
    except Exception as e:
        logger.error(f"Error onboarding manager: {str(e)}")
        raise HTTPException(status_code=500, detail="Error onboarding manager")

@app.get("/managers", response_model=List[Manager])
def list_managers():
    return managers

@app.get("/managers/{manager_id}/employees")
def get_manager_employees(manager_id: str):
    manager = next((m for m in managers if m.id == manager_id), None)
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return [emp for emp in employees if emp.id in manager.team_member_ids]

# -------------------------------------------------
# Employees
# -------------------------------------------------
@app.post("/employees")
def create_employee(employee: Employee):
    employee.id = str(uuid4())
    employees.append(employee)
    logger.info(f"Employee added: {employee.name}")
    return {"id": employee.id, "message": "Employee created successfully"}

@app.get("/employees", response_model=List[Employee])
def list_employees(manager_id: Optional[str] = None):
    if manager_id:
        manager = next((m for m in managers if m.id == manager_id), None)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        return [emp for emp in employees if emp.id in manager.team_member_ids]
    return employees

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    employee = next((e for e in employees if e.id == employee_id), None)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# -------------------------------------------------
# Projects (derived from Managers)
# -------------------------------------------------
@app.get("/projects")
def list_projects():
    """List all projects based on managers' projects."""
    projects = [{"id": m.id, "name": m.project} for m in managers]
    return projects

@app.get("/projects/{project_id}/employees")
def list_project_employees(project_id: str):
    """Get employees under a project (via manager)."""
    manager = next((m for m in managers if m.id == project_id), None)
    if not manager:
        raise HTTPException(status_code=404, detail="Project/Manager not found")
    return [emp for emp in employees if emp.id in manager.team_member_ids]

# -------------------------------------------------
# Nominations
# -------------------------------------------------
@app.post("/nominations")
def submit_nomination(nomination: Nomination):
    nomination.id = str(uuid4())
    nomination.created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    nominations.append(nomination)
    logger.info(f"Nomination submitted for {nomination.nominee_id}")
    return nomination

@app.get("/nominations/empty-form")
def get_nomination_form_template():
    return {
        "project_name": "",
        "justification_text": "",
        "customer_email": "",
        "core_value": "",
        "rating": 0,
        "nominee_id": ""
    }

@app.get("/nominations/{nomination_id}")
def get_nomination(nomination_id: str):
    nomination = next((n for n in nominations if n.id == nomination_id), None)
    if not nomination:
        raise HTTPException(status_code=404, detail="Nomination not found")
    return nomination

@app.patch("/nominations/{nomination_id}")
def update_nomination(nomination_id: str, updates: dict):
    for nom in nominations:
        if nom.id == nomination_id:
            for key, value in updates.items():
                setattr(nom, key, value)
            logger.info(f"Nomination {nomination_id} updated")
            return {"message": "Nomination updated successfully"}
    logger.warning(f"Nomination {nomination_id} not found")
    raise HTTPException(status_code=404, detail="Nomination not found")

@app.put("/nominations/{nomination_id}")
def replace_nomination(nomination_id: str, nomination: Nomination):
    for i, n in enumerate(nominations):
        if n.id == nomination_id:
            nomination.id = nomination_id
            nomination.created_at = n.created_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            nominations[i] = nomination
            logger.info(f"Nomination {nomination_id} replaced")
            return {"message": "Nomination replaced successfully"}
    raise HTTPException(status_code=404, detail="Nomination not found")

@app.get("/nominations", response_model=List[Nomination])
def list_nominations(
    search: Optional[str] = None,
    department: Optional[str] = None,
    period: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    is_winner: Optional[bool] = None
):
    data = nominations

    if search:
        data = [n for n in data if search.lower() in n.justification_text.lower()]
    if is_winner is not None:
        data = [n for n in data if n.is_winner == is_winner]

    start = (page - 1) * limit
    end = start + limit
    logger.info(f"Listing nominations page={page}, limit={limit}")
    return data[start:end]

# -------------------------------------------------
# Winners
# -------------------------------------------------
@app.get("/winners/monthly")
def winners_monthly():
    return [n for n in nominations if n.is_winner and "monthly" in n.project_name.lower()]

@app.get("/winners/quarterly")
def winners_quarterly():
    return [n for n in nominations if n.is_winner and "quarterly" in n.project_name.lower()]

@app.get("/winners/yearly")
def winners_yearly():
    return [n for n in nominations if n.is_winner and "yearly" in n.project_name.lower()]

# -------------------------------------------------
# Trends
# -------------------------------------------------
@app.get("/nominations/trends")
def get_trends():
    return {
        "month_change": "+12%",
        "quarter_change": "-5%",
        "year_change": "+30%"
    }

# -------------------------------------------------
# Reports
# -------------------------------------------------
@app.get("/reports/nominations")
def report_nominations():
    return {"total": len(nominations)}

@app.get("/reports/nominations/download")
def download_report(format: str = Query("csv", enum=["csv", "pdf"])):
    return {"message": f"Report generated in {format}"}

# -------------------------------------------------
# Metrics
# -------------------------------------------------
@app.get("/metrics")
def metrics():
    return {"uptime": "100%", "requests": len(nominations)}

# -------------------------------------------------
# Count APIs
# -------------------------------------------------
@app.get("/count/employees")
def count_employees():
    """Get total number of employees"""
    try:
        count = len(employees)
        logger.info(f"Total employees count requested: {count}")
        return {"total_employees": count}
    except Exception as e:
        logger.error(f"Error fetching employees count: {e}")
        raise HTTPException(status_code=500, detail="Error fetching employees count")


@app.get("/count/managers")
def count_managers():
    """Get total number of managers"""
    try:
        count = len(managers)
        logger.info(f"Total managers count requested: {count}")
        return {"total_managers": count}
    except Exception as e:
        logger.error(f"Error fetching managers count: {e}")
        raise HTTPException(status_code=500, detail="Error fetching managers count")

