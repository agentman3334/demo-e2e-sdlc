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

## SDLC Agentic Pipeline

This project was built end-to-end by a 10-step agentic SDLC pipeline powered by **Huawei Cloud CodeArts** AI agents and official MCP servers.

### Agents

| Agent | Responsibility |
|-------|---------------|
| **PM Agent** | Requirement breakdown, sprint management, release review (PR Merge Gate), deployment, sprint close |
| **Frontend Agent** | React UI development, component integration tests |
| **Backend Agent** | FastAPI development, API tests, database models |
| **Code Reviewer Agent** | Semgrep security/quality scanning, secret scanning, sign-off |
| **DevOps Agent** | CI/CD pipeline (GitHub Actions), JFrog Artifactory verification, SonarCloud scanning |
| **Tester Agent** | E2E testing via Microsoft Playwright skill, bug reporting |

### MCP Servers (Official)

| Server | Purpose |
|--------|---------|
| **Atlassian Rovo MCP** | Jira issue management, sprint operations, comments |
| **GitHub MCP** | Repository operations, PRs, file management |
| **SonarQube MCP** | Quality Gate, code issues, security hotspots, coverage |
| **Semgrep MCP** | Local security & quality scanning |
| **JFrog MCP** | Artifact verification, Xray security, build info |

### Skills (Official)

| Skill | Purpose |
|-------|---------|
| **Microsoft Playwright CLI** | E2E test automation — browser interactions, snapshots, assertions |

### Pipeline Steps

1. **Requirement Breakdown** → 1b. **Requirement Review** (gate) → 2. **Sprint Start & SDD Setup** → 3. **Development & Fix** → 4. **Code Review** → 5. **CI/CD Pipeline** → 5b. **JFrog Verification** → 6. **SonarCloud Scanning** → 7. **E2E Testing** (Playwright) → 8. **Release Review** (PR Merge Gate) → 9. **Huawei Cloud ECS Deployment** → 10. **Sprint Close**

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Ant Design 5, Axios |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose + passlib) |
| Deployment | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions, JFrog Artifactory, SonarCloud |
| E2E Testing | Microsoft Playwright |
