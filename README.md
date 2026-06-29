# Project Management System

A full-stack Project Management System built with React.js (Vite + Ant Design) frontend and Python (FastAPI) backend.

## Features

- User authentication (JWT-based login/register)
- Project CRUD with team member management
- Kanban-style task board with drag-and-drop
- Dashboard with progress tracking and analytics
- Role-based access control (Admin, Project Manager, Member)

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Database

Requires PostgreSQL 15+. Update `DATABASE_URL` in `backend/.env`.

Run migrations:

```bash
cd backend
alembic upgrade head
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Ant Design 5, Axios |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose + passlib) |
| Deployment | Docker, Docker Compose, Nginx |
