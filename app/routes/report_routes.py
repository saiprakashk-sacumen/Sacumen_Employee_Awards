from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Nomination, Employee, User, SentimentResult
from sqlalchemy import func, extract
from datetime import datetime
from app.db import get_db
import pandas as pd
import io

router = APIRouter(prefix="/reports", tags=["Reports"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Reports"]) 

@router.get("/download")
def download_report(format: str = "csv"):
    """
    Download nominations report in CSV or PDF.
    Example: /reports/download?format=csv
    """
    session = SessionLocal()
    try:
        # Fetch nominations with employee and manager info
        nominations = (
            session.query(Nomination, Employee, User)
            .join(Employee, Nomination.nominee_id == Employee.id)
            .join(User, Nomination.manager_id == User.id)
            .all()
        )

        data = []
        for nom, emp, mgr in nominations:
            data.append({
                "Nomination ID": nom.id,
                "Project": nom.project_name,
                "Employee Name": emp.name,
                "Employee Email": emp.email,
                "Manager Name": mgr.name,
                "Manager Email": mgr.email,
                "Core Value": nom.core_value,
                "Rating": nom.rating,
                "Justification": nom.justification_text,
                "Created At": nom.created_at
            })

        df = pd.DataFrame(data)

        if format.lower() == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=nominations_report.csv"}
            )
        elif format.lower() == "pdf":
            import pdfkit
            html = df.to_html(index=False)
            pdf = pdfkit.from_string(html, False)
            return StreamingResponse(
                iter([pdf]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=nominations_report.pdf"}
            )
        else:
            return {"error": "Invalid format"}
    finally:
        session.close()
    



@dashboard_router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    year, month = now.year, now.month

    # --- This month nomination count
    this_month_count = db.query(func.count(Nomination.id))\
        .filter(extract("year", Nomination.created_at) == year)\
        .filter(extract("month", Nomination.created_at) == month)\
        .scalar()

    # --- Last month nomination count
    last_month = month - 1 if month > 1 else 12
    last_month_year = year if month > 1 else year - 1
    last_month_count = db.query(func.count(Nomination.id))\
        .filter(extract("year", Nomination.created_at) == last_month_year)\
        .filter(extract("month", Nomination.created_at) == last_month)\
        .scalar()

    # --- Trending %
    trending = 0
    if last_month_count > 0:
        trending = ((this_month_count - last_month_count) / last_month_count) * 100

    # --- Average sentiment this month
    avg_sentiment = db.query(func.avg(SentimentResult.sentiment_score))\
        .filter(extract("year", SentimentResult.analyzed_at) == year)\
        .filter(extract("month", SentimentResult.analyzed_at) == month)\
        .scalar() or 0

    # --- Quarterly nominations (current quarter)
    quarter = (month - 1) // 3 + 1
    start_quarter = datetime(year, 3 * quarter - 2, 1)
    end_quarter = datetime(year, 3 * quarter + 1, 1) if quarter < 4 else datetime(year+1, 1, 1)
    quarterly_count = db.query(func.count(Nomination.id))\
        .filter(Nomination.created_at >= start_quarter, Nomination.created_at < end_quarter)\
        .scalar()

    # --- Yearly nominations
    yearly_count = db.query(func.count(Nomination.id))\
        .filter(extract("year", Nomination.created_at) == year)\
        .scalar()

    # --- Monthly nomination trends (last 6 months)
    monthly_trends = db.query(
        extract("month", Nomination.created_at).label("month"),
        func.count(Nomination.id).label("count")
    ).filter(extract("year", Nomination.created_at) == year)\
     .group_by("month")\
     .all()

    monthly_trends_dict = {int(m): c for m, c in monthly_trends}

    # --- Average sentiment trends (last 6 months)
    sentiment_trends = db.query(
        extract("month", SentimentResult.analyzed_at).label("month"),
        func.avg(SentimentResult.sentiment_score).label("avg_score")
    ).filter(extract("year", SentimentResult.analyzed_at) == year)\
     .group_by("month")\
     .all()

    sentiment_trends_dict = {int(m): float(avg or 0) for m, avg in sentiment_trends}

    return {
        "this_month_nominations": this_month_count,
        "last_month_nominations": last_month_count,
        "quarterly_nominations": quarterly_count,
        "yearly_nominations": yearly_count,
        "trending_percentage": trending,
        "average_sentiment_this_month": round(avg_sentiment, 2),
        "monthly_nomination_trends": monthly_trends_dict,
        "average_sentiment_trends": sentiment_trends_dict,
    }
