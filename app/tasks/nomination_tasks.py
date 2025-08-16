import json
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
import psycopg2

def load_employees():
    # Database connection details
    DB_HOST = "13.126.209.15"
    DB_PORT = 5454
    DB_NAME = "managers"
    DB_USER = "testuser"
    DB_PASS = "testpass"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )

        # Create cursor
        cur = conn.cursor()

        # Retrieve only the "manager_email" column
        cur.execute("SELECT manager_email FROM sacumen_managers;")  
        
        # Fetch all values from that column
        emails = cur.fetchall()

        # psycopg2 returns tuples, so extract the values
        emails = [row[0] for row in emails]

        # Close cursor and connection
        cur.close()
        conn.close()

        return emails

    except Exception as e:
        print("Database connection failed:", e)
        return []

# Call the function and store the emails in a variable
# managers_emails = load_employees()
# print("Loaded emails:", managers_emails)



# ---------------- EMAIL FUNCTION ----------------
def send_email(subject, body, recipients):
    sender_email = "hsgaming00007@gmail.com"
    sender_password = "mdgetxecjebvbjou"  # use App Password, not normal password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())

    # print(f"📧 Email sent to {len(recipients)} recipients.")

# ---------------- LOAD EMPLOYEES ----------------
# def load_employees():
#     with open("emp_data.json", "r") as f:
#         return json.load(f)

# ---------------- MONTHLY NOMINATION PROCESS ----------------
def send_monthly_nomination_start():
    # Load employees from JSON or database
    # employees = load_employees()  
    # managers = list({emp["manager_email"] for emp in employees if emp.get("manager_email")})
    managers = load_employees()
    subject = "Nomination Process Started"
    body = (
        "Hello Managers,\n\n"
        "The nomination process for this month has started.\n"
        "Please submit your nominations before the 25th.\n\n"
        "Best Regards,\nHR Department"
    )


    # Send to all managers at once
    send_email(subject, body, managers)
    print(f"Nomination start email sent to: {', '.join(managers)}")

def send_monthly_nomination_reminder():
    # employees = load_employees()  

    # managers = list({emp["manager_email"] for emp in employees if emp.get("manager_email")})
    managers = load_employees()
    subject = "Reminder: Employee Nomination Process"
    body = (
        "Hello Managers,\n\n"
        "This is a reminder to submit nominations for your employees before the end of the month.\n\n"
        "Best Regards,\nHR Department"
    )
    send_email(subject, body, managers)




# ---------------- QUARTERLY NOMINATION PROCESS ----------------

def send_quarterly_nomination_start():
    # employees = load_employees()  
    # managers = list({emp["manager_email"] for emp in employees if emp.get("manager_email")})
    managers = load_employees()
    subject = "Quarterly Nomination Process Started"
    body = (
        "Hello Managers,\n\n"
        "The nomination process for this quarter has started.\n"
        "Please review your employees and submit nominations.\n\n"
        "Best Regards,\nHR Department"
    )
    send_email(subject, body, managers)
    print(f"[{datetime.now()}] Quarterly START email sent to: {', '.join(managers)}")


def send_quarterly_nomination_reminder():
    # employees = load_employees()  
    # managers = list({emp["manager_email"] for emp in employees if emp.get("manager_email")})
    managers = load_employees()
    subject = "Quarterly Nomination Process Reminder"
    body = (
        "Hello Managers,\n\n"
        "This is a friendly reminder to complete your nominations before the quarter ends.\n\n"
        "Best Regards,\nHR Department"
    )
    send_email(subject, body, managers)
    print(f"[{datetime.now()}] Quarterly REMINDER email sent to: {', '.join(managers)}")


# ----------------- YEARLY NOMINATION PROCESS ----------------

def send_yearly_nomination_start():
    managers = load_employees()  # loads manager emails from DB
    subject = "Annual Nomination Process Started"
    body = (
        "Hello Managers,\n\n"
        "The annual employee awards nomination process has officially started.\n"
        "Please review your employees’ performance and submit your nominations before the deadline.\n\n"
        "Best Regards,\nHR Department"
    )
    send_email(subject, body, managers)
    print(f"[{datetime.now()}] YEARLY START email sent to: {', '.join(managers)}")



def send_yearly_nomination_reminder():
    employees = load_employees()  # loads all employees from DB or JSON

    # Extract unique manager emails
    managers = list({emp["manager_email"] for emp in employees if emp.get("manager_email")})

    subject = "Reminder: Annual Nomination Process"
    body = (
        "Hello Managers,\n\n"
        "This is a reminder to complete and submit your annual nominations before the deadline.\n\n"
        "Best Regards,\nHR Department"
    )

    send_email(subject, body, managers)
    print(f"[{datetime.now()}] YEARLY REMINDER email sent to: {', '.join(managers)}")


# # ---------------- Monthly Scheduler ----------------
scheduler = BackgroundScheduler()
now = datetime.now()

# Send start email on 1st day of month at 09:00 AM
scheduler.add_job(send_monthly_nomination_start, "cron", day=1, hour=9, minute=0)
# scheduler.add_job(send_monthly_nomination_start, "date", run_date=now + timedelta(minutes=1))
# scheduler.add_job(send_monthly_nomination_start, "interval", minutes=1)


# Send reminder email on 25th day of month at 09:00 AM
scheduler.add_job(send_monthly_nomination_reminder, "cron", day=25, hour=9, minute=0)
# scheduler.add_job(send_monthly_nomination_reminder, "date", run_date=now + timedelta(minutes=5))


# -------------------- Quarterly Scheduler ----------------
# Start email → Jan 1, Apr 1, Jul 1, Oct 1 at 11 AM
scheduler.add_job(send_quarterly_nomination_start, "cron", month="1,4,7,10", day=1, hour=11, minute=0)
# scheduler.add_job(send_quarterly_nomination_start, "date", run_date=now)


# Reminder email → Mar 25, Jun 25, Sep 25, Dec 25 at 11 AM
scheduler.add_job(send_quarterly_nomination_reminder, "cron", month="3,6,9,12", day=25, hour=11, minute=0)
# scheduler.add_job(send_quarterly_nomination_reminder, "date", run_date=now + timedelta(minutes=2))


# -------------------- Yearly Scheduler ----------------
scheduler.add_job(send_yearly_nomination_start, "cron", month=1, day=1, hour=10, minute=0)
# scheduler.add_job(send_yearly_nomination_start, "interval", minutes=1)

scheduler.add_job(send_yearly_nomination_reminder, 'cron', month=12, day=25, hour=10, minute=0)



scheduler.start()

print("✅ Scheduler started... Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")