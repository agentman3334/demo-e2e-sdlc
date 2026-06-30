<div align="center">

# Project Management System

**Agentic DevOps Pipeline — From Requirements to Production, Fully Automated**

> Demonstrate an agentic DevOps pipeline flow where a primary **PM Agent** orchestrates subagents — using official MCP servers and Skills — to automate the full software development lifecycle from requirements to deployment.

A full-stack Project Management System built with React.js (Vite + Ant Design) frontend and Python (FastAPI) backend.

[![CI/CD](https://github.com/agentman3334/demo-e2e-sdlc/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/agentman3334/demo-e2e-sdlc/actions/workflows/ci-cd.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=agentman3334_demo-e2e-sdlc&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=agentman3334_demo-e2e-sdlc)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=agentman3334_demo-e2e-sdlc&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=agentman3334_demo-e2e-sdlc)
[![Reliability](https://sonarcloud.io/api/project_badges/measure?project=agentman3334_demo-e2e-sdlc&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=agentman3334_demo-e2e-sdlc)

</div>

---

## Features

- 🔐 User authentication (JWT-based login/register)
- 📋 Project CRUD with team member management
- 📌 Kanban-style task board with drag-and-drop
- 📊 Dashboard with progress tracking and analytics
- 👥 Role-based access control (Admin, Project Manager, Member)

---

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### Manual Setup

<details>
<summary>Backend</summary>

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

</details>

<details>
<summary>Frontend</summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

<details>
<summary>Database</summary>

Requires PostgreSQL 15+. Update `DATABASE_URL` in `backend/.env`.

```bash
cd backend
alembic upgrade head
```

</details>

---

## SDLC Agentic Pipeline

This project was built end-to-end by a **10-step agentic SDLC pipeline** powered by [Huawei Cloud CodeArts Agent](https://www.huaweicloud.com/intl/en-us/product/codearts/ai.html) and official MCP servers.

### Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         AGENTIC DEVOPS PIPELINE                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────┐   ┌──────┐   ┌─────┐   ┌─────────────┐   ┌─────┐   ┌──────┐         │
│  │  1  │──▶│  1b  │──▶│  2  │──▶│      3      │──▶│  4  │──▶│  5   │         │
│  │ Req │   │ Rev  │   │Sprnt│   │ Development │   │ CR  │   │CI/CD │         │
│  │Break│   │Gate🔒│   │ SDD │   │   & Fix     │   │Scan │   │      │          │
│  └─────┘   └──────┘   └─────┘   └─────────────┘   └─────┘   └──┬───┘         │
│     PM       FE/BE       PM        FE/BE Agent      CR Agent   DevOps        │
│    Agent     Agent      Agent                                   Agent        │
│                                                                              │
│  ┌──────┐   ┌─────┐   ┌──────────┐   ┌─────┐   ┌──────────┐   ┌─────┐        │
│  │  5b  │──▶│  6  │──▶│    7     │──▶│  8  │──▶│    9     │──▶│ 10  │        │
│  │JFrog│   │Sonar│   │   E2E    │   │Rel  │   │  Deploy  │   │Close│         │
│  │ Vrfy│   │Cloud│   │ Testing  │   │ Rev │   │  Huawei  │   │ Sprt│         │
│  └──────┘   └─────┘   └──────────┘   └─────┘   └──────────┘   └─────┘        │
│  DevOps     DevOps      Tester         PM 🔒      PM 🔒         PM             │
│  Agent      Agent       Agent          Agent       Agent        Agent        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Agents

| Agent | Role | Responsibility |
|-------|------|---------------|
| **PM Agent** | Primary 🎯 | Requirement breakdown, sprint management, release review (PR Merge Gate), deployment, sprint close |
| **Frontend Agent** | Subagent | React UI development, component integration tests |
| **Backend Agent** | Subagent | FastAPI development, API tests, database models |
| **Code Reviewer Agent** | Subagent | Semgrep security/quality scanning, secret scanning, sign-off |
| **DevOps Agent** | Subagent | CI/CD pipeline (GitHub Actions), JFrog Artifactory verification, SonarCloud scanning |
| **Tester Agent** | Subagent | E2E testing via Microsoft Playwright skill, bug reporting |

### MCP Servers (Official)

| Server | Purpose |
|--------|---------|
| 🟦 **Atlassian Rovo MCP** | Jira issue management, sprint operations, comments |
| ⬛ **GitHub MCP** | Repository operations, PRs, file management |
| 🟧 **SonarQube MCP** | Quality Gate, code issues, security hotspots, coverage |
| 🟪 **Semgrep MCP** | Local security & quality scanning |
| 🟩 **JFrog MCP** | Artifact verification, Xray security, build info |

### Skills (Official)

| Skill | Purpose |
|-------|---------|
| 🎭 **Microsoft Playwright CLI** | E2E test automation — browser interactions, snapshots, assertions |


---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| 🖥️ Frontend | React 18, Vite, Ant Design 5, Axios |
| ⚙️ Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic |
| 🗄️ Database | PostgreSQL 15 |
| 🔐 Auth | JWT (python-jose + passlib) |
| 🐳 Deployment | Docker, Docker Compose, Nginx |
| 🔄 CI/CD | GitHub Actions, JFrog Artifactory, SonarCloud |
| 🧪 E2E Testing | Microsoft Playwright |
