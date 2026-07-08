# Habit Tracker

A full stack habit tracking web app built with **FastAPI** (backend) and **plain HTML/CSS/JavaScript** (frontend). Register an account, add daily habits, check them off each day, and watch your streaks grow.

---

## Features

- **User accounts** — register and log in with email and password
- **JWT authentication** — protected endpoints, tokens stored in the browser
- **Habit management** — create, complete, and delete habits
- **Streak tracking** — consecutive day streaks calculated from completion history
- **Daily check-off** — idempotent, safe to call multiple times on the same day
- **Clean dashboard** — dark UI with streak numbers as the visual centrepiece

---

## Project structure

```
habit-tracker/
  backend/
    app/
      models/
        models.py        SQLAlchemy table definitions (User, Habit, HabitLog)
      routers/
        auth.py          POST /auth/register, POST /auth/login
        habits.py        Habit CRUD + completion endpoints
      schemas/
        schemas.py       Pydantic request/response models
      auth.py            Password hashing (bcrypt) and JWT utilities
      database.py        SQLAlchemy engine, session, and Base
      main.py            FastAPI app entry point
    requirements.txt
    .env                 (not committed — see setup below)
  frontend/
    index.html           Login / register page
    dashboard.html       Habit dashboard
    style.css
```

---

## Running it locally

**1. PostgreSQL**

Install PostgreSQL and create the database:

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres psql
```

Inside psql:
```sql
CREATE DATABASE habittracker;
ALTER USER postgres WITH PASSWORD 'your-password';
\q
```

**2. Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
```
DATABASE_URL=postgresql://postgres:your-password@localhost:5432/habittracker
SECRET_KEY=change-this-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Start the server:
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

SQLAlchemy will create the database tables automatically on first run.

**3. Frontend**

Open `frontend/index.html` directly in a browser. It connects to the backend at `http://localhost:8000`.

---

## API overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Create a new account |
| POST | `/auth/login` | — | Log in, receive JWT token |
| GET | `/habits` | ✓ | List all habits with streaks |
| POST | `/habits` | ✓ | Create a habit |
| PATCH | `/habits/{id}` | ✓ | Update habit name or description |
| DELETE | `/habits/{id}` | ✓ | Delete a habit and its history |
| POST | `/habits/{id}/complete` | ✓ | Mark habit done today |
| DELETE | `/habits/{id}/complete` | ✓ | Unmark habit for today |
| GET | `/habits/{id}/logs` | ✓ | Get full completion history |

Interactive API docs available at `http://localhost:8000/docs` when the server is running.

---

## How it works

**Password hashing** — passwords are hashed with bcrypt before storage. The plain text password never touches the database.

**JWT auth** — on login the server signs a token containing the user's email. Every protected request sends this token in the `Authorization: Bearer` header. The server verifies the signature without hitting the database.

**Streak calculation** — streaks are computed at query time from the `habit_logs` table, not stored. The logic walks backwards from today through consecutive completed dates.

**Idempotent check-off** — `POST /habits/{id}/complete` checks for an existing log entry before inserting, so calling it twice on the same day is safe.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, uvicorn |
| Database | PostgreSQL, SQLAlchemy ORM |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Frontend | HTML, CSS, vanilla JavaScript |
