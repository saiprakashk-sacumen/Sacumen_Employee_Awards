import json
import os
from app.db import SessionLocal
from app.models import Employee

def seed_employees(json_file="app/emp_project.json"):
    if not os.path.exists(json_file):
        print(f"{json_file} not found, skipping seeding.")
        return

    db = SessionLocal()

    with open(json_file) as f:
        data = json.load(f)

    for emp in data:   # ✅ JSON is a list of employees
        exists = db.query(Employee).filter(Employee.id == emp["employee_id"]).first()
        if not exists:
            new_emp = Employee(
                id=emp["employee_id"],          # JSON employee_id → id
                name=emp["employee_name"],      # JSON employee_name → name
                email=emp["employee_email"],    # JSON employee_email → email
                project=emp["project_name"],    # JSON project_name → project
                manager_id=None                 # set None unless you want to map later
            )
            db.add(new_emp)

    db.commit()
    db.close()
    print("Employees seeded successfully.")
