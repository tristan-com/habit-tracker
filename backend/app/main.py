"""
Habit Tracker API — entry point.

Registers routers, sets up CORS, and creates database tables on startup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, habits

# Import models so SQLAlchemy registers them with Base before create_all
from app.models import models  # noqa: F401

app = FastAPI(title="Habit Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock this down to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables that don't exist yet.
# In production you'd use Alembic migrations instead, but this is fine for development.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(habits.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Habit Tracker API"}