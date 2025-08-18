from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import User
from email.mime.text import MIMEText
import smtplib
import os

# ----------------- Email function -----------------
def send_email(subject: str, body: str, recipients: list[str]):
    sender_email = "prasanna.sekar@gmail.com"
    sender_password = "your-app-password"


    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())

# ----------------- DB Helper -----------------
def get_managers(session: Session):
    return session.query(User).filter(User.role == "manager", User.is_approved == True).all()

# ----------------- Nomination Email Jobs -----------------
def send_nomination_email(subject: str, body: str):
    session = SessionLocal()
    try:
        managers = get_managers(session)
        emails = [m.email for m in managers]
        if emails:
            send_email(subject, body, emails)
            print(f"[{datetime.now()}] Email sent to {len(emails)} managers: {subject}")
        else:
            print(f"[{datetime.now()}] No managers found to send email.")
    finally:
        session.close()

def monthly_nomination_reminder():
    subject = "Reminder: Monthly Nomination Process"
    body = "Hello Managers,\n\nReminder to submit nominations before 25th of this month.\n\nHR Department"
    send_nomination_email(subject, body)

def quarterly_nomination_reminder():
    subject = "Reminder: Quarterly Nomination Process"
    body = "Hello Managers,\n\nReminder to submit nominations for this quarter before 25th.\n\nHR Department"
    send_nomination_email(subject, body)

def yearly_nomination_reminder():
    subject = "Reminder: Yearly Nomination Process"
    body = "Hello Managers,\n\nReminder to submit nominations for this year before 25th December.\n\nHR Department"
    send_nomination_email(subject, body)

def test_email_job():
    subject = "Test Email from Nomination Scheduler"
    body = "Hello Prasanna,\n\nThis is a test email sent every 5 minutes.\n\nIgnore this email."
    send_email(subject, body, ["prasanna.sekar@sacumen.com"])
    print(f"[{datetime.now()}] Test email sent to prasanna.sekar@sacumen.com")

# ----------------- Scheduler -----------------
scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(monthly_nomination_reminder, "cron", day=25, hour=9, minute=0)
    scheduler.add_job(quarterly_nomination_reminder, "cron", month="3,6,9,12", day=25, hour=10, minute=0)
    scheduler.add_job(yearly_nomination_reminder, "cron", month=12, day=25, hour=11, minute=0)
    scheduler.add_job(test_email_job, "interval", minutes=5)
    scheduler.start()
    print("✅ Email Scheduler started...")
