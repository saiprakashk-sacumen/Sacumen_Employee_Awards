from fastapi import FastAPI
from app import auth  # import auth.py
from app.routes import ai_routes
from app.db import engine, Base
from app.models import * 
from app.db_seed import seed_superadmin

app = FastAPI(title="Auth Service")


# Create all tables in the database (for dev / first run)
Base.metadata.create_all(bind=engine)

# Include auth router
app.include_router(auth.router)

app.include_router(ai_routes.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    seed_superadmin()