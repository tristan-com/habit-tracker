"""
Database models.

Each class here maps to one table in Postgres. SQLAlchemy reads these
class definitions to know how to create tables, run queries, and map
rows back to Python objects.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # One user has many habits. 'cascade' means deleting a user
    # also deletes all their habits automatically.
    habits = relationship("Habit", back_populates="owner", cascade="all, delete")


class Habit(Base):
    __tablename__ = "habits"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    name        = Column(String, nullable=False)
    description = Column(String, default="")
    created_at  = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="habits")
    logs  = relationship("HabitLog", back_populates="habit", cascade="all, delete")


class HabitLog(Base):
    """
    One row = one day a habit was completed.

    We store just the date (not datetime) so checking off "today" is
    idempotent — calling it twice on the same day doesn't create duplicates
    because we check for an existing row first.
    """
    __tablename__ = "habit_logs"

    id             = Column(Integer, primary_key=True, index=True)
    habit_id       = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completed_date = Column(Date, nullable=False, default=date.today)

    habit = relationship("Habit", back_populates="logs")