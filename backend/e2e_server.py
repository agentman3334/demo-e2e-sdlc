"""
E2E test server - completely independent from app.database module.
Creates its own SQLite engine and patches the dependency injection.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase

# Create our own SQLite engine - DO NOT import app.database
DB_PATH = os.path.abspath("test_e2e.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables for testing."""
    # Import models to register them with THIS Base
    # We need to re-define the models using our Base class
    import uuid
    from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func

    from datetime import timezone as _tz

    class User(Base):
        __tablename__ = "users"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = Column(String(255), unique=True, nullable=False, index=True)
        hashed_password = Column(String(255), nullable=False)
        full_name = Column(String(100), nullable=False)
        role = Column(String(20), default="member")
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=lambda: datetime.now(_tz.utc))
        updated_at = Column(DateTime, default=lambda: datetime.now(_tz.utc), onupdate=lambda: datetime.now(_tz.utc))

    class Project(Base):
        __tablename__ = "projects"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        name = Column(String(200), nullable=False)
        description = Column(Text, nullable=True)
        status = Column(String(20), default="active")
        deadline = Column(DateTime, nullable=True)
        owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
        is_deleted = Column(Boolean, default=False)
        created_at = Column(DateTime, default=lambda: datetime.now(_tz.utc))
        updated_at = Column(DateTime, default=lambda: datetime.now(_tz.utc), onupdate=lambda: datetime.now(_tz.utc))

    class ProjectMember(Base):
        __tablename__ = "project_members"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
        user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
        role = Column(String(20), default="member")
        joined_at = Column(DateTime, default=lambda: datetime.now(_tz.utc))

    class Task(Base):
        __tablename__ = "tasks"
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
        title = Column(String(300), nullable=False)
        description = Column(Text, nullable=True)
        status = Column(String(20), default="todo")
        priority = Column(String(10), default="medium")
        assignee_id = Column(String(36), ForeignKey("users.id"), nullable=True)
        due_date = Column(DateTime, nullable=True)
        is_deleted = Column(Boolean, default=False)
        created_at = Column(DateTime, default=lambda: datetime.now(_tz.utc))
        updated_at = Column(DateTime, default=lambda: datetime.now(_tz.utc), onupdate=lambda: datetime.now(_tz.utc))

    # Store model classes for later use
    globals()['User'] = User
    globals()['Project'] = Project
    globals()['ProjectMember'] = ProjectMember
    globals()['Task'] = Task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Initialize DB - use a single event loop run
# IMPORTANT: Only call asyncio.run() ONCE, then let uvicorn manage the loop
async def _init_and_serve():
    await init_db()
    print("DB initialized with SQLite")
    
    import uvicorn
    print("Starting E2E test server on http://localhost:8000")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(_init_and_serve())
# We need to patch the routers' dependency on get_db
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, func

# Config
SECRET_KEY = "e2e-test-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas
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

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    deadline: Optional[datetime] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PaginatedProjectResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    size: int

class ProjectMemberAdd(BaseModel):
    user_id: str
    role: Optional[str] = "member"

class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: str
    joined_at: datetime
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskStatusUpdate(BaseModel):
    status: str

class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PaginatedTaskResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    size: int


# Auth helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    from datetime import timedelta, timezone
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    from datetime import timedelta, timezone
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    User = globals()['User']
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def require_role(*roles):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# CRUD helpers
async def get_or_404(db, model, entity_id, name="Entity"):
    result = await db.execute(select(model).where(model.id == entity_id, model.is_deleted == False))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return entity

async def apply_update(db, entity, update_schema):
    update_data = update_schema.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)
    await db.flush()
    return entity

async def soft_delete(db, entity):
    entity.is_deleted = True
    await db.flush()
    return entity

async def paginated_list(db, base_query, page=1, size=20):
    offset = (page - 1) * size
    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0
    result = await db.execute(base_query.offset(offset).limit(size))
    items = list(result.scalars().all())
    return {"items": items, "total": total, "page": page, "size": size}


# Create FastAPI app
app = FastAPI(title="PMS E2E Test Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === AUTH ROUTES ===
@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        User = globals()['User']
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    User = globals()['User']
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    token_data = {"sub": user.id, "role": user.role}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_token(token_in: TokenRefresh, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token_in.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    User = globals()['User']
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    token_data = {"sub": user.id, "role": user.role}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user

@app.put("/api/auth/me", response_model=UserResponse)
async def update_me(user_in: UserUpdate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    update_data = user_in.model_dump(exclude_unset=True)
    if "email" in update_data:
        User = globals()['User']
        result = await db.execute(select(User).where(User.email == update_data["email"]))
        existing = result.scalar_one_or_none()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user

# === PROJECT ROUTES ===
@app.get("/api/projects/", response_model=PaginatedProjectResponse)
async def list_projects(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    base_query = (
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == current_user.id, Project.is_deleted == False)
        .order_by(Project.created_at.desc())
    )
    return await paginated_list(db, base_query, page, size)

@app.post("/api/projects/", response_model=ProjectResponse, status_code=201)
async def create_project(project_in: ProjectCreate, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    project = Project(name=project_in.name, description=project_in.description, deadline=project_in.deadline, owner_id=current_user.id)
    db.add(project)
    await db.flush()
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role="project_manager")
    db.add(member)
    await db.flush()
    await db.refresh(project)
    return project

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    project = await get_or_404(db, Project, project_id, "Project")
    result = await db.execute(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id))
    if not result.scalar_one_or_none() and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not a project member")
    return project

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_in: ProjectUpdate, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    project = await get_or_404(db, Project, project_id, "Project")
    return await apply_update(db, project, project_in)

@app.delete("/api/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, current_user=Depends(require_role("admin",)), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    project = await get_or_404(db, Project, project_id, "Project")
    await soft_delete(db, project)

@app.post("/api/projects/{project_id}/members", response_model=ProjectMemberResponse, status_code=201)
async def add_member(project_id: str, member_in: ProjectMemberAdd, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    User = globals()['User']
    await get_or_404(db, Project, project_id, "Project")
    result = await db.execute(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == member_in.user_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")
    result = await db.execute(select(User).where(User.id == member_in.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    member = ProjectMember(project_id=project_id, user_id=member_in.user_id, role=member_in.role)
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member

@app.delete("/api/projects/{project_id}/members/{user_id}", status_code=204)
async def remove_member(project_id: str, user_id: str, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    ProjectMember = globals()['ProjectMember']
    result = await db.execute(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in project")
    await db.delete(member)
    await db.flush()

# === TASK ROUTES ===
@app.get("/api/tasks/", response_model=PaginatedTaskResponse)
async def list_tasks(project_id: Optional[str] = None, status: Optional[str] = None, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Task = globals()['Task']
    query = select(Task).where(Task.is_deleted == False)
    if project_id:
        query = query.where(Task.project_id == project_id)
    if status:
        query = query.where(Task.status == status)
    query = query.order_by(Task.created_at.desc())
    return await paginated_list(db, query, page, size)

@app.post("/api/tasks/projects/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(project_id: str, task_in: TaskCreate, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    Task = globals()['Task']
    await get_or_404(db, Project, project_id, "Project")
    task = Task(project_id=project_id, title=task_in.title, description=task_in.description, priority=task_in.priority, assignee_id=task_in.assignee_id, due_date=task_in.due_date)
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Task = globals()['Task']
    return await get_or_404(db, Task, task_id, "Task")

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_in: TaskUpdate, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Task = globals()['Task']
    task = await get_or_404(db, Task, task_id, "Task")
    if current_user.role == "member" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
    return await apply_update(db, task, task_in)

@app.patch("/api/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: str, status_in: TaskStatusUpdate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Task = globals()['Task']
    task = await get_or_404(db, Task, task_id, "Task")
    if current_user.role == "member" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
    valid_statuses = ["todo", "in_progress", "in_review", "done"]
    if status_in.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    task.status = status_in.status
    await db.flush()
    await db.refresh(task)
    return task

@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str, current_user=Depends(require_role("admin", "project_manager")), db: AsyncSession = Depends(get_db)):
    Task = globals()['Task']
    task = await get_or_404(db, Task, task_id, "Task")
    await soft_delete(db, task)

# === ANALYTICS ROUTES ===
@app.get("/api/analytics/dashboard")
async def dashboard_stats(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    Task = globals()['Task']
    project_ids_query = select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
    project_ids_result = await db.execute(project_ids_query)
    project_ids = [row[0] for row in project_ids_result.all()]
    if not project_ids:
        return {"total_tasks": 0, "completed": 0, "in_progress": 0, "overdue": 0, "projects": []}
    total_result = await db.execute(select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.is_deleted == False))
    total_tasks = total_result.scalar()
    completed_result = await db.execute(select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.status == "done", Task.is_deleted == False))
    completed = completed_result.scalar()
    in_progress_result = await db.execute(select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.status == "in_progress", Task.is_deleted == False))
    in_progress = in_progress_result.scalar()
    from datetime import timezone as tz
    now = datetime.now(tz.utc)
    overdue_result = await db.execute(select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.status != "done", Task.is_deleted == False, Task.due_date < now))
    overdue = overdue_result.scalar()
    projects_result = await db.execute(select(Project).where(Project.id.in_(project_ids), Project.is_deleted == False))
    projects = []
    for project in projects_result.scalars().all():
        p_total = await db.execute(select(func.count(Task.id)).where(Task.project_id == project.id, Task.is_deleted == False))
        p_done = await db.execute(select(func.count(Task.id)).where(Task.project_id == project.id, Task.status == "done", Task.is_deleted == False))
        t = p_total.scalar() or 0
        d = p_done.scalar() or 0
        projects.append({"id": project.id, "name": project.name, "status": project.status, "progress": round((d / t) * 100) if t > 0 else 0})
    return {"total_tasks": total_tasks, "completed": completed, "in_progress": in_progress, "overdue": overdue, "projects": projects}

@app.get("/api/analytics/project/{project_id}")
async def project_stats(project_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    Project = globals()['Project']
    ProjectMember = globals()['ProjectMember']
    Task = globals()['Task']
    result = await db.execute(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id))
    if not result.scalar_one_or_none() and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not a project member")
    project_result = await db.execute(select(Project).where(Project.id == project_id, Project.is_deleted == False))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    total_result = await db.execute(select(func.count(Task.id)).where(Task.project_id == project_id, Task.is_deleted == False))
    total_tasks = total_result.scalar() or 0
    status_counts = {}
    for s in ["todo", "in_progress", "in_review", "done"]:
        r = await db.execute(select(func.count(Task.id)).where(Task.project_id == project_id, Task.status == s, Task.is_deleted == False))
        status_counts[s] = r.scalar() or 0
    priority_counts = {}
    for p in ["low", "medium", "high", "critical"]:
        r = await db.execute(select(func.count(Task.id)).where(Task.project_id == project_id, Task.priority == p, Task.is_deleted == False))
        priority_counts[p] = r.scalar() or 0
    from datetime import timezone as tz
    now = datetime.now(tz.utc)
    overdue_result = await db.execute(select(func.count(Task.id)).where(Task.project_id == project_id, Task.status != "done", Task.is_deleted == False, Task.due_date < now))
    overdue = overdue_result.scalar() or 0
    return {"project_id": project_id, "project_name": project.name, "total_tasks": total_tasks, "status_counts": status_counts, "priority_counts": priority_counts, "overdue": overdue, "progress": round((status_counts.get("done", 0) / total_tasks) * 100) if total_tasks > 0 else 0}

# === TEST HELPER ROUTES ===
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/test/reset-db")
async def test_reset_db():
    await reset_db()
    return {"status": "reset"}

@app.post("/test/set-role")
async def set_role(data: dict, db: AsyncSession = Depends(get_db)):
    User = globals()['User']
    result = await db.execute(select(User).where(User.id == data["user_id"]))
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}
    user.role = data["role"]
    await db.flush()
    return {"user_id": user.id, "role": user.role}


if __name__ == "__main__":
    import uvicorn
    print("Starting E2E test server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")