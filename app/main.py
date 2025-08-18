from fastapi import FastAPI
from app import auth  # import auth.py
from app.routes import ai_routes, nomination_routes
from app.db import engine, Base
from app.models import * 
from app.db_seed import seed_superadmin
from app.seed_emp import seed_employees
from fastapi.middleware.cors import CORSMiddleware
from app.routes import project_routes, employee_routes, manager_routes, nomination_routes




from app.routes import project_routes, employee_routes, manager_routes, nomination_routes, report_routes, prometheus_routes
from app.routes import ai_routes


app = FastAPI(title="Auth Service", redirect_slashes=True)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- This allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create all tables in the database (for dev / first run)
Base.metadata.create_all(bind=engine)



# ----------------- CORS Setup -----------------
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:8000",               # API URL exposed by Docker
    "https://your-frontend-domain.com"    # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# Create all tables in the database (for dev / first run)
Base.metadata.create_all(bind=engine)

# Include auth router
app.include_router(auth.router)
app.include_router(ai_routes.router)
app.include_router(manager_routes.router)
app.include_router(project_routes.router)
app.include_router(employee_routes.router)
app.include_router(nomination_routes.router)
app.include_router(report_routes.router)
app.include_router(prometheus_routes.router)


app.include_router(ai_routes.router)

app.include_router(manager_routes.router)

app.include_router(project_routes.router)
app.include_router(employee_routes.router)
app.include_router(nomination_routes.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    seed_superadmin()
    seed_employees()

