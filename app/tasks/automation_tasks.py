import json
import random

# -------------------
# Data Generators
# -------------------

def generate_slack_data(emp_id):
    channels = ["#engineering", "#product", "#random", "#hackathon", "#support"]
    
    return {
        "messages_sent": random.randint(20, 200),
        "reactions_given": random.randint(5, 50),
        "reactions_received": random.randint(1, 20),
        "channels_active": random.sample(channels, random.randint(1, len(channels))),
        "sentiment_scores": [round(random.uniform(-1, 1), 2) for _ in range(5)],  # -1 = negative, 1 = positive
        "message_texts": [f"Sample message {i}" for i in range(5)]
    }

def generate_jira_data(emp_id):
    tickets = []
    ticket_prefix = random.choice(["ENG", "PROD", "OPS", "HR", "FIN"])
    num_tickets = random.randint(2, 8)
    for _ in range(num_tickets):
        ticket_id = f"{ticket_prefix}-{random.randint(100, 999)}"
        hours = round(random.uniform(1, 12), 1)
        tickets.append({"ticket_id": ticket_id, "hours_spent": hours})

    return {
        "jira_user": emp_id,
        "tickets": tickets,
        "total_hours": sum(t["hours_spent"] for t in tickets)
    }

def generate_extra_activities():
    activities = [
        "Hackathon Winner",
        "AWS Certified",
        "Azure Certified",
        "GCP Certified",
        "Helping Interview Panel",
        "Organized Team Building",
        "Mentorship Program"
    ]
    return random.sample(activities, k=random.randint(1, 3))

def generate_sacufit():
    return {
        "bmi": round(random.uniform(18.0, 28.0), 1),
        "fitness_level": random.choice(["Excellent", "Good", "Average"])
    }

def generate_annual_day():
    events = ["Dance Performance", "Singing", "Comedy Skit", "Drama Play", "Event Host"]
    return random.sample(events, k=random.randint(0, 2))

# -------------------
# Employee Generator
# -------------------

def generate_employees(n=100):
    first_names = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Kavya", "Aditya", "Neha", "Manish", "Shreya"]
    last_names = ["Mehta", "Sharma", "Iyer", "Patel", "Gupta", "Nair", "Reddy", "Joshi", "Kumar", "Bose"]
    departments = ["Engineering", "Product", "Marketing", "HR", "Finance"]

    employees = []
    for i in range(1, n + 1):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        emp_id = f"EMP{i:03d}"
        email = f"{fname.lower()}.{lname.lower()}@company.com"

        emp = {
            "employee_id": emp_id,
            "name": f"{fname} {lname}",
            "email": email,
            "department": random.choice(departments),
            "slack_data": generate_slack_data(emp_id),
            "jira_data": generate_jira_data(emp_id),
            "extra_activities": generate_extra_activities(),
            "sacufit": generate_sacufit(),
            "annual_day_participation": generate_annual_day(),
        }
        employees.append(emp)

    return employees


if __name__ == "__main__":
    employees = generate_employees(100)
    with open("employees.json", "w") as f:
        json.dump(employees, f, indent=2)

    print("✅ employees.json generated with Slack + Jira + Extra Activities + Sacufit + Annual Day (now includes Slack active hours)")
