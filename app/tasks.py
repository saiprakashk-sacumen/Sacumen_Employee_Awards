from .tasks.email_scheduler import (
    monthly_nomination_start,
    monthly_nomination_reminder,
    # quarterly and yearly functions...
)
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Monthly
scheduler.add_job(monthly_nomination_start, "cron", day=1, hour=9, minute=0)
scheduler.add_job(monthly_nomination_reminder, "cron", day=25, hour=9, minute=0)

# Quarterly
scheduler.add_job(quarterly_nomination_start, "cron", month="1,4,7,10", day=1, hour=11)
scheduler.add_job(quarterly_nomination_reminder, "cron", month="3,6,9,12", day=25, hour=11)

# Yearly
scheduler.add_job(yearly_nomination_start, "cron", month=1, day=1, hour=10)
scheduler.add_job(yearly_nomination_reminder, "cron", month=12, day=25, hour=10)

scheduler.start()
print("✅ Email Scheduler started...")
