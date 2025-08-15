from fastapi import FastAPI
from app import auth  # import auth.py

app = FastAPI(title="Auth Service")

# Include auth router
app.include_router(auth.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
