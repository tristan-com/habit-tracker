"""
Pydantic schemas.

These define the shape of data coming IN to the API (request bodies)
and going OUT (response bodies). They are separate from the SQLAlchemy
models deliberately:

  - SQLAlchemy models describe the database structure
  - Pydantic schemas describe the API contract

This separation means we can expose different fields than what's stored
(e.g. never expose hashed_password in a response) and validate incoming
data before it ever touches the database.
"""

from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional


# ---- User ----

class UserCreate(BaseModel):
    """What the client sends when registering."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """What we send back — note: no password field."""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True   # allows building from SQLAlchemy model objects


# ---- Auth ----

class Token(BaseModel):
    """The JWT token returned after a successful login."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """What we store inside the JWT payload."""
    email: Optional[str] = None


# ---- Habit ----

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class HabitResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    streak: int = 0              # calculated, not stored in DB
    completed_today: bool = False

    class Config:
        from_attributes = True


# ---- HabitLog ----

class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    completed_date: date

    class Config:
        from_attributes = True