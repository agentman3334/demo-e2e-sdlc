# Technical Design Document: Project Management System

## 1. Document Information

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Author | AI Data Turkiye 2026 |
| Date | 2026-06-29 |
| Status | Draft |
| Audience | Development Team |

---

## 2. Background and Objectives

### 2.1 Background

Project management is a universal challenge across organizations of all sizes. Teams need a centralized platform to plan projects, assign tasks, track progress, and collaborate effectively. Existing solutions like Jira and Asana are feature-rich but often overly complex for small-to-medium teams and come with significant licensing costs.

### 2.2 Objectives

- Build a lightweight, self-hosted Project Management System (PMS) using a React.js + Python (FastAPI) stack
- Provide core PM functionalities: authentication, project CRUD, task assignment, and progress tracking
- Deliver a clean, responsive UI with real-time status updates
- Ensure the system is extensible for future enhancements (notifications, file uploads, Gantt charts)

---

## 3. Core Features

### 3.1 User Authentication & Authorization

| Feature | Description |
|---------|-------------|
| Registration | Email + password signup with input validation |
| Login | JWT-based authentication with access + refresh tokens |
| Role Management | Three roles: `Admin`, `Project Manager`, `Member` |
| Profile | View/edit user profile, change password |

### 3.2 Project Management

| Feature | Description |
|---------|-------------|
| Create Project | Title, description, deadline, assigned team members |
| List Projects | Dashboard view with filters (status, owner, date) |
| Update Project | Edit details, change status (Active / On Hold / Completed / Archived) |
| Delete Project | Soft delete with confirmation dialog |
| Project Members | Add/remove team members to a project |

### 3.3 Task Management

| Feature | Description |
|---------|-------------|
| Create Task | Title, description, assignee, priority, due date, project |
| Task Board | Kanban-style board with columns: To Do, In Progress, In Review, Done |
| Drag & Drop | Move tasks between columns to update status |
| Task Details | Full task view with comments, attachments placeholder |
| Task Filters | Filter by assignee, priority, project, due date |

### 3.4 Progress Tracking

| Feature | Description |
|---------|-------------|
| Dashboard Metrics | Total tasks, completed, in-progress, overdue counts |
| Project Progress | Percentage completion per project |
| Burndown Chart | Visual representation of task completion over time |
| Activity Feed | Recent actions across projects and tasks |

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              React.js (Vite)                     │
│  ┌──────────┬──────────┬──────────┬───────────┐ │
│  │  Auth    │ Project  │  Task    │ Dashboard  │ │
│  │  Module  │ Module   │  Module  │ Module     │ │
│  └────┬─────┴────┬─────┴────┬─────┴─────┬─────┘ │
│       └──────────┴──────────┴───────────┘        │
│                    │ Axios HTTP                   │
└────────────────────┼────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────┼────────────────────────────┐
│                    ▼           Backend           │
│              FastAPI (Python)                    │
│  ┌──────────┬──────────┬──────────┬───────────┐ │
│  │  Auth    │ Project  │  Task    │ Analytics  │ │
│  │  Router  │ Router   │  Router  │ Router     │ │
│  └────┬─────┴────┬─────┴────┬─────┴─────┬─────┘ │
│       └──────────┴──────────┴───────────┘        │
│                    │ SQLAlchemy ORM               │
│              ┌─────┴─────┐                       │
│              │ PostgreSQL │                       │
│              └───────────┘                       │
└──────────────────────────────────────────────────┘
```

### 4.2 Directory Structure

#### Backend (FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings via pydantic
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User ORM model
│   │   ├── project.py           # Project ORM model
│   │   └── task.py              # Task ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # Pydantic request/response schemas
│   │   ├── project.py
│   │   └── task.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # /api/auth/* endpoints
│   │   ├── projects.py          # /api/projects/* endpoints
│   │   ├── tasks.py             # /api/tasks/* endpoints
│   │   └── analytics.py         # /api/analytics/* endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # JWT creation, password hashing
│   │   ├── project_service.py   # Business logic for projects
│   │   └── task_service.py      # Business logic for tasks
│   └── utils/
│       ├── __init__.py
│       └── dependencies.py      # get_current_user, get_db
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_auth.py
│   ├── test_projects.py
│   └── test_tasks.py
├── requirements.txt
├── alembic.ini
└── Dockerfile
```

#### Frontend (React.js + Vite)

```
frontend/
├── public/
├── src/
│   ├── main.jsx                 # React entry point
│   ├── App.jsx                  # Root component with router
│   ├── api/
│   │   ├── axios.js             # Axios instance with interceptors
│   │   ├── authApi.js           # Auth API calls
│   │   ├── projectApi.js        # Project API calls
│   │   └── taskApi.js           # Task API calls
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Input.jsx
│   │   │   └── Spinner.jsx
│   │   ├── layout/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── AppLayout.jsx
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   └── RegisterForm.jsx
│   │   ├── project/
│   │   │   ├── ProjectCard.jsx
│   │   │   ├── ProjectList.jsx
│   │   │   └── ProjectForm.jsx
│   │   ├── task/
│   │   │   ├── TaskCard.jsx
│   │   │   ├── TaskBoard.jsx
│   │   │   ├── TaskColumn.jsx
│   │   │   └── TaskForm.jsx
│   │   └── dashboard/
│   │       ├── StatsCard.jsx
│   │       ├── BurndownChart.jsx
│   │       └── ActivityFeed.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── ProjectsPage.jsx
│   │   ├── ProjectDetailPage.jsx
│   │   └── TaskBoardPage.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useProjects.js
│   │   └── useTasks.js
│   ├── context/
│   │   └── AuthContext.jsx       # Auth state provider
│   ├── utils/
│   │   └── constants.js
│   └── styles/
│       └── index.css
├── index.html
├── vite.config.js
├── package.json
└── Dockerfile
```

### 4.3 RESTful API Endpoint Design

#### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login, returns JWT tokens | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| GET | `/api/auth/me` | Get current user profile | Yes |
| PUT | `/api/auth/me` | Update current user profile | Yes |

#### Projects

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/api/projects` | List user's projects | Yes | Any |
| POST | `/api/projects` | Create project | Yes | PM, Admin |
| GET | `/api/projects/{id}` | Get project details | Yes | Member |
| PUT | `/api/projects/{id}` | Update project | Yes | PM, Admin |
| DELETE | `/api/projects/{id}` | Soft delete project | Yes | Admin |
| POST | `/api/projects/{id}/members` | Add member to project | Yes | PM, Admin |
| DELETE | `/api/projects/{id}/members/{uid}` | Remove member | Yes | PM, Admin |

#### Tasks

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| GET | `/api/tasks?project_id=&status=` | List tasks with filters | Yes | Any |
| POST | `/api/projects/{id}/tasks` | Create task in project | Yes | PM, Admin |
| GET | `/api/tasks/{id}` | Get task details | Yes | Member |
| PUT | `/api/tasks/{id}` | Update task | Yes | Assignee, PM, Admin |
| PATCH | `/api/tasks/{id}/status` | Update task status only | Yes | Assignee, PM, Admin |
| DELETE | `/api/tasks/{id}` | Delete task | Yes | PM, Admin |

#### Analytics

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/analytics/dashboard` | Dashboard stats (counts, progress) | Yes |
| GET | `/api/analytics/burndown?project_id=` | Burndown chart data | Yes |
| GET | `/api/analytics/activity` | Recent activity feed | Yes |

### 4.4 Database Schema

#### Entity-Relationship Overview

```
┌──────────────┐       ┌───────────────────┐       ┌──────────────┐
│    users      │       │ project_members   │       │   projects   │
├──────────────┤       ├───────────────────┤       ├──────────────┤
│ id (PK)      │──┐    │ id (PK)           │    ┌──│ id (PK)      │
│ email        │  │    │ user_id (FK)      │────┘  │ name         │
│ hashed_pw    │  └────│ project_id (FK)   │───────│ description  │
│ full_name    │       │ role               │       │ status       │
│ role         │       └───────────────────┘       │ deadline     │
│ is_active    │                                    │ owner_id(FK) │
│ created_at   │                                    │ created_at   │
│ updated_at   │                                    │ updated_at   │
└──────────────┘                                    └──────┬───────┘
                                                           │
                                                    ┌──────┴───────┐
                                                    │    tasks      │
                                                    ├──────────────┤
                                                    │ id (PK)      │
                                                    │ project_id(FK)│
                                                    │ title        │
                                                    │ description  │
                                                    │ status       │
                                                    │ priority     │
                                                    │ assignee_id(FK)│
                                                    │ due_date     │
                                                    │ created_at   │
                                                    │ updated_at   │
                                                    └──────────────┘
```

#### SQL DDL

`users` table:

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(100) | NOT NULL |
| role | VARCHAR(20) | DEFAULT 'member', CHECK IN ('admin','project_manager','member') |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

`projects` table:

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| name | VARCHAR(200) | NOT NULL |
| description | TEXT | |
| status | VARCHAR(20) | DEFAULT 'active', CHECK IN ('active','on_hold','completed','archived') |
| deadline | TIMESTAMP | |
| owner_id | UUID | FK -> users.id, NOT NULL |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

`project_members` table:

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| project_id | UUID | FK -> projects.id, NOT NULL |
| user_id | UUID | FK -> users.id, NOT NULL |
| role | VARCHAR(20) | DEFAULT 'member', CHECK IN ('project_manager','member') |
| joined_at | TIMESTAMP | DEFAULT NOW() |
| | | UNIQUE(project_id, user_id) |

`tasks` table:

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| project_id | UUID | FK -> projects.id, NOT NULL |
| title | VARCHAR(300) | NOT NULL |
| description | TEXT | |
| status | VARCHAR(20) | DEFAULT 'todo', CHECK IN ('todo','in_progress','in_review','done') |
| priority | VARCHAR(10) | DEFAULT 'medium', CHECK IN ('low','medium','high','critical') |
| assignee_id | UUID | FK -> users.id, NULLABLE |
| due_date | TIMESTAMP | |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

---

## 5. Core Technology Selection and Rationale

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React.js 18 + Vite | Fast HMR, mature ecosystem, large talent pool |
| UI Library | Ant Design 5 | Production-grade components, built-in theming |
| State Management | React Context + useReducer | Sufficient for this scope; avoids Redux overhead |
| HTTP Client | Axios | Interceptors for JWT, request/response transform |
| Backend | FastAPI (Python 3.11+) | Async support, auto-generated OpenAPI docs, type safety |
| ORM | SQLAlchemy 2.0 (async) | Mature, supports async, migration via Alembic |
| Database | PostgreSQL 15 | ACID compliance, JSON support, UUID native type |
| Auth | JWT (python-jose) | Stateless, scalable, industry standard |
| Migrations | Alembic | Tight SQLAlchemy integration |
| Containerization | Docker + Docker Compose | Consistent dev/prod environments |

---

## 6. Implementation Guide

### 6.1 Backend Initialization

#### Step 1: Project Setup

Create the backend directory and install dependencies:

`requirements.txt`:

    fastapi==0.104.1
    uvicorn[standard]==0.24.0
    sqlalchemy[asyncio]==2.0.23
    asyncpg==0.29.0
    alembic==1.13.0
    python-jose[cryptography]==3.3.0
    passlib[bcrypt]==1.7.4
    pydantic==2.5.2
    pydantic-settings==2.1.0
    python-multipart==0.0.6

#### Step 2: Configuration

`app/config.py`:

    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pms"
        SECRET_KEY: str = "your-secret-key-change-in-production"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        REFRESH_TOKEN_EXPIRE_DAYS: int = 7

        class Config:
            env_file = ".env"

    settings = Settings()

#### Step 3: Database Setup

`app/database.py`:

    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy.orm import DeclarativeBase
    from app.config import settings

    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    class Base(DeclarativeBase):
        pass

    async def get_db():
        async with async_session() as session:
            yield session

#### Step 4: User Model

`app/models/user.py`:

    import uuid
    from sqlalchemy import Column, String, Boolean, DateTime, func
    from sqlalchemy.orm import relationship
    from app.database import Base

    class User(Base):
        __tablename__ = "users"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = Column(String(255), unique=True, nullable=False, index=True)
        hashed_password = Column(String(255), nullable=False)
        full_name = Column(String(100), nullable=False)
        role = Column(String(20), default="member")
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, server_default=func.now())
        updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

        tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
        owned_projects = relationship("Project", back_populates="owner")

#### Step 5: Auth Router

`app/routers/auth.py`:

    from datetime import datetime, timedelta, timezone
    from fastapi import APIRouter, Depends, HTTPException, status
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from jose import jwt, JWTError
    from passlib.context import CryptContext
    from app.database import get_db
    from app.models.user import User
    from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
    from app.config import settings

    router = APIRouter(prefix="/api/auth", tags=["auth"])
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=user_in.email,
            hashed_password=pwd_context.hash(user_in.password),
            full_name=user_in.full_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @router.post("/login", response_model=Token)
    async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User).where(User.email == user_in.email))
        user = result.scalar_one_or_none()
        if not user or not pwd_context.verify(user_in.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token_data = {"sub": user.id, "role": user.role}
        return Token(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            token_type="bearer",
        )

#### Step 6: FastAPI App Entry Point

`app/main.py`:

    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.routers import auth, projects, tasks, analytics

    app = FastAPI(title="Project Management System", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(projects.router)
    app.include_router(tasks.router)
    app.include_router(analytics.router)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

Run the server:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### 6.2 Frontend Implementation

#### Step 1: Project Initialization

    npm create vite@latest frontend -- --template react
    cd frontend
    npm install axios react-router-dom antd @ant-design/icons dayjs

#### Step 2: Axios Instance with JWT Interceptors

`src/api/axios.js`:

    import axios from 'axios';

    const api = axios.create({
      baseURL: 'http://localhost:8000',
      headers: { 'Content-Type': 'application/json' },
    });

    api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const { data } = await axios.post('http://localhost:8000/api/auth/refresh', {
                refresh_token: refreshToken,
              });
              localStorage.setItem('access_token', data.access_token);
              originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
              return api(originalRequest);
            } catch {
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );

    export default api;

#### Step 3: Auth Context

`src/context/AuthContext.jsx`:

    import { createContext, useContext, useState, useEffect } from 'react';
    import authApi from '../api/authApi';

    const AuthContext = createContext(null);

    export function AuthProvider({ children }) {
      const [user, setUser] = useState(null);
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
          authApi.getMe().then(({ data }) => setUser(data)).catch(() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }).finally(() => setLoading(false));
        } else {
          setLoading(false);
        }
      }, []);

      const login = async (credentials) => {
        const { data } = await authApi.login(credentials);
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        const me = await authApi.getMe();
        setUser(me.data);
      };

      const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      };

      return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
          {children}
        </AuthContext.Provider>
      );
    }

    export const useAuth = () => useContext(AuthContext);

#### Step 4: Task Board Component (Kanban)

`src/components/task/TaskBoard.jsx`:

    import { useState, useEffect } from 'react';
    import { Row, Col, Card, Tag, Avatar, Typography } from 'antd';
    import { UserOutlined } from '@ant-design/icons';
    import taskApi from '../../api/taskApi';

    const COLUMNS = [
      { key: 'todo', label: 'To Do', color: 'default' },
      { key: 'in_progress', label: 'In Progress', color: 'processing' },
      { key: 'in_review', label: 'In Review', color: 'warning' },
      { key: 'done', label: 'Done', color: 'success' },
    ];

    const PRIORITY_COLORS = {
      low: 'blue',
      medium: 'orange',
      high: 'red',
      critical: 'magenta',
    };

    export default function TaskBoard({ projectId }) {
      const [tasks, setTasks] = useState([]);

      useEffect(() => {
        if (projectId) {
          taskApi.list({ project_id: projectId }).then(({ data }) => setTasks(data));
        }
      }, [projectId]);

      const handleStatusChange = async (taskId, newStatus) => {
        await taskApi.updateStatus(taskId, { status: newStatus });
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
        );
      };

      return (
        <Row gutter={16}>
          {COLUMNS.map((col) => (
            <Col span={6} key={col.key}>
              <Typography.Title level={5}>
                <Tag color={col.color}>{col.label}</Tag>
                {tasks.filter((t) => t.status === col.key).length}
              </Typography.Title>
              <div
                style={{ minHeight: 400, padding: 8, background: '#fafafa', borderRadius: 8 }}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  const taskId = e.dataTransfer.getData('taskId');
                  handleStatusChange(taskId, col.key);
                }}
              >
                {tasks
                  .filter((t) => t.status === col.key)
                  .map((task) => (
                    <Card
                      key={task.id}
                      size="small"
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('taskId', task.id)}
                      style={{ marginBottom: 8, cursor: 'grab' }}
                    >
                      <Typography.Text strong>{task.title}</Typography.Text>
                      <div style={{ marginTop: 8 }}>
                        <Tag color={PRIORITY_COLORS[task.priority]}>{task.priority}</Tag>
                        {task.assignee && (
                          <Avatar size="small" icon={<UserOutlined />} />
                        )}
                      </div>
                    </Card>
                  ))}
              </div>
            </Col>
          ))}
        </Row>
      );
    }

#### Step 5: Dashboard Page

`src/pages/DashboardPage.jsx`:

    import { useEffect, useState } from 'react';
    import { Row, Col, Card, Statistic, Typography } from 'antd';
    import {
      CheckCircleOutlined,
      ClockCircleOutlined,
      ExclamationCircleOutlined,
      ProjectOutlined,
    } from '@ant-design/icons';
    import analyticsApi from '../api/analyticsApi';

    export default function DashboardPage() {
      const [stats, setStats] = useState({ total_tasks: 0, completed: 0, in_progress: 0, overdue: 0 });

      useEffect(() => {
        analyticsApi.getDashboard().then(({ data }) => setStats(data));
      }, []);

      return (
        <div>
          <Typography.Title level={3}>Dashboard</Typography.Title>
          <Row gutter={16}>
            <Col span={6}>
              <Card><Statistic title="Total Tasks" value={stats.total_tasks} prefix={<ProjectOutlined />} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title="Completed" value={stats.completed} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#3f8600' }} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title="In Progress" value={stats.in_progress} prefix={<ClockCircleOutlined />} valueStyle={{ color: '#1890ff' }} /></Card>
            </Col>
            <Col span={6}>
              <Card><Statistic title="Overdue" value={stats.overdue} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#cf1322' }} /></Card>
            </Col>
          </Row>
        </div>
      );
    }

### 6.3 Frontend-Backend Integration

#### API Service Modules

`src/api/authApi.js`:

    import api from './axios';

    export default {
      register: (data) => api.post('/api/auth/register', data),
      login: (data) => api.post('/api/auth/login', data),
      refresh: (data) => api.post('/api/auth/refresh', data),
      getMe: () => api.get('/api/auth/me'),
      updateMe: (data) => api.put('/api/auth/me', data),
    };

`src/api/projectApi.js`:

    import api from './axios';

    export default {
      list: (params) => api.get('/api/projects', { params }),
      create: (data) => api.post('/api/projects', data),
      get: (id) => api.get(`/api/projects/${id}`),
      update: (id, data) => api.put(`/api/projects/${id}`, data),
      delete: (id) => api.delete(`/api/projects/${id}`),
      addMember: (projectId, data) => api.post(`/api/projects/${projectId}/members`, data),
      removeMember: (projectId, userId) => api.delete(`/api/projects/${projectId}/members/${userId}`),
    };

`src/api/taskApi.js`:

    import api from './axios';

    export default {
      list: (params) => api.get('/api/tasks', { params }),
      create: (projectId, data) => api.post(`/api/projects/${projectId}/tasks`, data),
      get: (id) => api.get(`/api/tasks/${id}`),
      update: (id, data) => api.put(`/api/tasks/${id}`, data),
      updateStatus: (id, data) => api.patch(`/api/tasks/${id}/status`, data),
      delete: (id) => api.delete(`/api/tasks/${id}`),
    };

#### Docker Compose for Full Stack

`docker-compose.yml`:

    version: "3.9"
    services:
      db:
        image: postgres:15
        environment:
          POSTGRES_DB: pms
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - "5432:5432"
        volumes:
          - pgdata:/var/lib/postgresql/data

      backend:
        build: ./backend
        ports:
          - "8000:8000"
        environment:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/pms
          SECRET_KEY: production-secret-key
        depends_on:
          - db

      frontend:
        build: ./frontend
        ports:
          - "5173:80"
        depends_on:
          - backend

    volumes:
      pgdata:

---

## 7. Data Flow / Call Chain Description

### 7.1 Authentication Flow

```
1. User submits credentials on LoginPage
2. LoginForm calls authApi.login(email, password)
3. Axios POSTs to /api/auth/login
4. FastAPI auth router validates credentials
5. On success: returns { access_token, refresh_token, token_type }
6. Frontend stores tokens in localStorage
7. Subsequent requests include Authorization: Bearer <token>
8. Backend dependencies.get_current_user decodes and validates JWT
9. If access token expired (401), interceptor attempts refresh
10. On refresh failure, redirect to /login
```

### 7.2 Task Status Update Flow (Drag & Drop)

```
1. User drags TaskCard from "To Do" column to "In Progress" column
2. onDrop handler calls taskApi.updateStatus(taskId, { status: 'in_progress' })
3. Axios PATCHes /api/tasks/{id}/status
4. FastAPI task router validates user has permission
5. SQLAlchemy updates task.status in PostgreSQL
6. Response returns updated task
7. Frontend updates local state (optimistic or confirmed)
8. Dashboard stats refresh on next visit
```

---

## 8. Non-Functional Design

### 8.1 Security

| Concern | Mitigation |
|---------|-----------|
| Password storage | bcrypt hashing via passlib |
| Token security | JWT with short-lived access tokens (30 min) + refresh tokens (7 days) |
| CORS | Whitelist frontend origin only |
| SQL injection | SQLAlchemy parameterized queries |
| Input validation | Pydantic schemas on all endpoints |
| Rate limiting | Add slowapi middleware (future) |

### 8.2 Performance

| Concern | Mitigation |
|---------|-----------|
| N+1 queries | Eager loading with `selectinload` where needed |
| Large result sets | Pagination (limit/offset) on all list endpoints |
| Static assets | Vite build optimization, gzip in production via Nginx |
| Database connections | Async connection pool via SQLAlchemy async engine |

### 8.3 Scalability

| Concern | Mitigation |
|---------|-----------|
| Horizontal scaling | Stateless JWT auth enables load balancing |
| Database scaling | Read replicas for analytics queries (future) |
| Caching | Redis for session data and frequent queries (future) |

---

## 9. Deployment Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │                         │
     ┌────────▼────────┐     ┌─────────▼─────────┐
     │  Frontend       │     │  Backend           │
     │  (Static build  │     │  (FastAPI +        │
     │   served by     │     │   Uvicorn workers) │
     │   Nginx)        │     │                    │
     └─────────────────┘     └─────────┬──────────┘
                                       │
                              ┌────────▼────────┐
                              │  PostgreSQL     │
                              │  (Persistent    │
                              │   Volume)       │
                              └─────────────────┘
```

---

## 10. Context and Analysis: React.js + Python Stack

### 10.1 Characteristics in Practical Applications

| Characteristic | Description |
|---------------|-------------|
| Separation of concerns | Frontend and backend are fully decoupled, enabling independent deployment and scaling |
| Type safety boundary | Pydantic on backend + PropTypes/TypeScript on frontend provide validation at API boundaries |
| Async-first | Both React (concurrent rendering) and FastAPI (async I/O) are designed for non-blocking operations |
| API-driven | All communication via REST/JSON; the backend serves as a pure API server |

### 10.2 Applicable Scenarios

| Scenario | Fit |
|----------|-----|
| Data-heavy dashboards and admin panels | Excellent - React component model + Python data processing |
| Startups and MVPs | Excellent - Rapid prototyping with FastAPI auto-docs and React hot reload |
| Internal tools for tech companies | Excellent - Python ecosystem for integrations (ML, data, automation) |
| Real-time collaboration tools | Good - Requires adding WebSocket layer (FastAPI supports natively) |
| High-traffic consumer applications | Moderate - Needs careful optimization; Python GIL can be a bottleneck for CPU-bound work |

### 10.3 Advantages

| Advantage | Detail |
|-----------|--------|
| Developer productivity | Python's concise syntax + React's declarative model accelerate development |
| Rich ecosystems | npm (React) and PyPI (Python) offer packages for virtually any need |
| Auto-documentation | FastAPI generates OpenAPI/Swagger docs automatically |
| Full-stack JavaScript alternative | Python brings ML/data science capabilities that Node.js lacks |
| Hiring pool | Both React and Python have large developer communities |

### 10.4 Disadvantages

| Disadvantage | Detail |
|-------------|--------|
| Two-language stack | Requires expertise in both JavaScript and Python; increases onboarding complexity |
| Deployment complexity | Two separate build pipelines and deployment processes |
| Python performance | Slower than Go/Rust for CPU-intensive tasks; GIL limits true parallelism |
| State management at scale | React Context/useReducer may not suffice for very large apps (would need Redux/Zustand) |
| Type safety gaps | Without TypeScript on frontend, type mismatches between frontend and backend can occur at runtime |

### 10.5 Comparison with Other Full-Stack Solutions

| Dimension | React + FastAPI | Next.js + Express | Django + React | Vue + Flask |
|-----------|----------------|-------------------|----------------|-------------|
| **Language** | JS + Python | JS only | Python + JS | JS + Python |
| **Learning Curve** | Medium (2 langs) | Low (1 lang) | High (Django ORM) | Medium |
| **API Docs** | Auto (Swagger) | Manual | Auto (DRF) | Manual |
| **Async Support** | Native | Native | Limited (Django 4+) | Limited |
| **Performance** | Good | Good | Moderate | Moderate |
| **ML/AI Integration** | Excellent | Poor | Excellent | Excellent |
| **SSR/SEO** | No (SPA only) | Yes (Next.js) | Yes (Django templates) | No (SPA only) |
| **Community Size** | Large | Very Large | Large | Medium |
| **Best For** | Data apps, APIs, MVPs | Full-stack JS, SEO apps | Content sites, admin | Lightweight tools |

**Summary**: The React + FastAPI stack excels in scenarios requiring rapid API development with strong data/ML integration. For pure web applications with SEO needs, Next.js is superior. For content-heavy sites with built-in admin, Django is more productive. The two-language overhead is the primary trade-off.

---

## 11. Risks and Open Decisions

| Risk | Impact | Mitigation |
|------|--------|-----------|
| JWT token theft | High | Short-lived access tokens, secure cookie option, HTTPS only in production |
| Scope creep | Medium | Strictly prioritize core features; defer Gantt, file uploads, notifications |
| Frontend-backend schema drift | Medium | Share OpenAPI spec; consider code generation (openapi-typescript) |
| Database migration failures | High | Test migrations in staging; always backup before production migration |

| Open Decision | Options | Recommendation |
|--------------|--------|----------------|
| TypeScript adoption | Plain JS vs TypeScript | Adopt TypeScript in Phase 2 for type safety |
| Real-time updates | Polling vs WebSocket vs SSE | WebSocket via FastAPI for Phase 2 |
| File storage | Local disk vs S3/MinIO | MinIO for self-hosted; S3 for cloud |
| Caching layer | None vs Redis | Add Redis when analytics queries slow down |

---

## Appendix A: Key Pydantic Schemas

`app/schemas/user.py`:

    from pydantic import BaseModel, EmailStr
    from datetime import datetime

    class UserCreate(BaseModel):
        email: EmailStr
        password: str
        full_name: str

    class UserLogin(BaseModel):
        email: EmailStr
        password: str

    class UserResponse(BaseModel):
        id: str
        email: str
        full_name: str
        role: str
        is_active: bool
        created_at: datetime

        class Config:
            from_attributes = True

    class Token(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str = "bearer"

## Appendix B: Key Dependencies (get_current_user)

`app/utils/dependencies.py`:

    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession
    from jose import jwt, JWTError
    from app.config import settings
    from app.database import get_db
    from app.models.user import User
    from sqlalchemy import select

    security = HTTPBearer()

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        try:
            payload = jwt.decode(
                credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user