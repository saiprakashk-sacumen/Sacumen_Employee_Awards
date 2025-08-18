from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Nomination, Employee, User
import pandas as pd
import io

router = APIRouter(prefix="/reports", tags=["Reports"])

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
    