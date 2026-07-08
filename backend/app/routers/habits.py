"""
Habit endpoints — all protected by JWT auth.

GET    /habits          list all habits for the logged-in user (with streak)
POST   /habits          create a new habit
PATCH  /habits/{id}     update name or description
DELETE /habits/{id}     delete a habit and all its logs

POST   /habits/{id}/complete     mark habit as done today
DELETE /habits/{id}/complete     unmark habit for today
GET    /habits/{id}/logs         get completion history
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Habit, HabitLog, User
from app.schemas.schemas import HabitCreate, HabitUpdate, HabitResponse, HabitLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/habits", tags=["habits"])


def calculate_streak(logs: list[HabitLog]) -> int:
    """
    Count how many consecutive days ending today (or yesterday) a habit
    was completed.

    We sort the completed dates descending, then walk back from today.
    If there's a gap, the streak is broken.

    We allow yesterday as the starting point so a streak doesn't reset
    just because the user hasn't checked in yet today.
    """
    if not logs:
        return 0

    completed_dates = sorted(
        {log.completed_date for log in logs},
        reverse=True
    )

    today     = date.today()
    yesterday = today - timedelta(days=1)

    # Streak must start from today or yesterday
    if completed_dates[0] not in (today, yesterday):
        return 0

    streak    = 0
    check_day = completed_dates[0]

    for completed in completed_dates:
        if completed == check_day:
            streak   += 1
            check_day = check_day - timedelta(days=1)
        elif completed < check_day:
            break   # gap found

    return streak


def build_habit_response(habit: Habit) -> HabitResponse:
    """Attach computed fields (streak, completed_today) to a habit."""
    today = date.today()
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description or "",
        created_at=habit.created_at,
        streak=calculate_streak(habit.logs),
        completed_today=any(log.completed_date == today for log in habit.logs),
    )


# ---- Habit CRUD ----

@router.get("", response_model=list[HabitResponse])
def list_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    return [build_habit_response(h) for h in habits]


@router.post("", response_model=HabitResponse, status_code=201)
def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = Habit(
        user_id=current_user.id,
        name=habit_in.name,
        description=habit_in.description or "",
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return build_habit_response(habit)


@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_in: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if habit_in.name is not None:
        habit.name = habit_in.name
    if habit_in.description is not None:
        habit.description = habit_in.description

    db.commit()
    db.refresh(habit)
    return build_habit_response(habit)


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()


# ---- Completion (HabitLog) ----

@router.post("/{habit_id}/complete", response_model=HabitLogResponse, status_code=201)
def complete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a habit as completed today. Idempotent — safe to call twice."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    today = date.today()
    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed_date == today,
    ).first()

    if existing:
        return existing   # already logged today, just return it

    log = HabitLog(habit_id=habit_id, completed_date=today)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{habit_id}/complete", status_code=204)
def uncomplete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Unmark a habit for today (undo accidental check-off)."""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    today = date.today()
    log = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed_date == today,
    ).first()

    if log:
        db.delete(log)
        db.commit()


@router.get("/{habit_id}/logs", response_model=list[HabitLogResponse])
def get_habit_logs(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit.logs