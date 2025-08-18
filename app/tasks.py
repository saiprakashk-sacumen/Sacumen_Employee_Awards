from apscheduler.schedulers.background import BackgroundScheduler
from .tasks.email_scheduler import (
    monthly_nomination_reminder,
    quarterly_nomination_reminder,
    yearly_nomination_reminder
)

scheduler = BackgroundScheduler()

# Monthly: 25th of every month
scheduler.add_job(monthly_nomination_reminder, "cron", day=25, hour=9, minute=0)

# Quarterly: 25th of quarter-end months (Mar, Jun, Sep, Dec)
scheduler.add_job(quarterly_nomination_reminder, "cron", month="3,6,9,12", day=25, hour=10, minute=0)

# Yearly: 25th December
scheduler.add_job(yearly_nomination_reminder, "cron", month=12, day=25, hour=11, minute=0)

scheduler.start()
print("✅ Email Scheduler started...")
