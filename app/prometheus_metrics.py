from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response

router = APIRouter()
# Example metrics
submissions_total = Counter("awards_submissions_total", "Total nominations submitted", ['cycle'])
employee_score_gauge = Gauge("employee_score", "Employee final score", ['employee_id'])

@router.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
