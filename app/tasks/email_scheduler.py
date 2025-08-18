from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from fastapi import Depends
from ..db import SessionLocal
from ..models import User
from email.mime.text import MIMEText
import smtplib
import os

# ----------------- Email function -----------------
def send_email(subject: str, body: str, recipients: list[str]):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())

# ----------------- DB Helper -----------------
def get_managers(session: Session):
    return session.query(User).filter(User.role == "manager").all()

# ----------------- Email Jobs -----------------
def monthly_nomination_start():
    session = SessionLocal()
    managers = get_managers(session)
    emails = [m.email for m in managers]

    subject = "Monthly Nomination Process Started"
    body = "Hello Managers,\n\nPlease submit your nominations before the 25th.\n\nHR Department"
    send_email(subject, body, emails)
    print(f"[{datetime.now()}] Monthly START email sent to {len(emails)} managers")
    session.close()

def monthly_nomination_reminder():
    session = SessionLocal()
    managers = get_managers(session)
    emails = [m.email for m in managers]

    subject = "Reminder: Monthly Nomination Process"
    body = "Hello Managers,\n\nReminder to submit nominations before the 25th.\n\nHR Department"
    send_email(subject, body, emails)
    print(f"[{datetime.now()}] Monthly REMINDER email sent to {len(emails)} managers")
    session.close()

# Similar functions for quarterly_nomination_start/reminder and yearly...
