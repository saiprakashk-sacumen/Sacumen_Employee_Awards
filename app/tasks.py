from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery = Celery("tasks", broker=redis_url, backend=redis_url)

@celery.task
def add(x, y):
    return x + y
