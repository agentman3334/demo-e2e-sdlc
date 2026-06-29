from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.task import Task
from app.models.project import Project, ProjectMember
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException, status
from datetime import datetime, timezone


async def create_task(db: AsyncSession, project_id: str, task_in: TaskCreate) -> Task:
    task = Task(
        project_id=project_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        assignee_id=task_in.assignee_id,
        due_date=task_in.due_date,
    )
    db.add(task)
    await db.flush()
    return task


async def get_task(db: AsyncSession, task_id: str) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.is_deleted == False))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def list_tasks(db: AsyncSession, project_id: str = None, status_filter: str = None, page: int = 1, size: int = 20) -> dict:
    offset = (page - 1) * size
    query = select(Task).where(Task.is_deleted == False)
    if project_id:
        query = query.where(Task.project_id == project_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    result = await db.execute(query.order_by(Task.created_at.desc()).offset(offset).limit(size))
    items = list(result.scalars().all())
    return {"items": items, "total": total, "page": page, "size": size}


async def update_task(db: AsyncSession, task: Task, task_in: TaskUpdate) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.flush()
    return task


async def update_task_status(db: AsyncSession, task: Task, new_status: str) -> Task:
    valid_statuses = ["todo", "in_progress", "in_review", "done"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    task.status = new_status
    await db.flush()
    return task


async def delete_task(db: AsyncSession, task: Task) -> None:
    task.is_deleted = True
    await db.flush()


async def get_dashboard_stats(db: AsyncSession, user_id: str) -> dict:
    project_ids_query = (
        select(ProjectMember.project_id)
        .where(ProjectMember.user_id == user_id)
    )
    project_ids_result = await db.execute(project_ids_query)
    project_ids = [row[0] for row in project_ids_result.all()]

    if not project_ids:
        return {"total_tasks": 0, "completed": 0, "in_progress": 0, "overdue": 0, "projects": []}

    total_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.is_deleted == False)
    )
    total_tasks = total_result.scalar()

    completed_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.status == "done", Task.is_deleted == False)
    )
    completed = completed_result.scalar()

    in_progress_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id.in_(project_ids), Task.status == "in_progress", Task.is_deleted == False)
    )
    in_progress = in_progress_result.scalar()

    now = datetime.now(timezone.utc)
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id.in_(project_ids),
            Task.status != "done",
            Task.is_deleted == False,
            Task.due_date < now,
        )
    )
    overdue = overdue_result.scalar()

    projects_result = await db.execute(
        select(Project).where(Project.id.in_(project_ids), Project.is_deleted == False)
    )
    projects = []
    for project in projects_result.scalars().all():
        p_total = await db.execute(
            select(func.count(Task.id)).where(Task.project_id == project.id, Task.is_deleted == False)
        )
        p_done = await db.execute(
            select(func.count(Task.id)).where(Task.project_id == project.id, Task.status == "done", Task.is_deleted == False)
        )
        total = p_total.scalar() or 0
        done = p_done.scalar() or 0
        projects.append({
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "progress": round((done / total) * 100) if total > 0 else 0,
        })

    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "overdue": overdue,
        "projects": projects,
    }


async def get_project_stats(db: AsyncSession, project_id: str) -> dict:
    project_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id == project_id, Task.is_deleted == False)
    )
    total_tasks = total_result.scalar() or 0

    status_counts = {}
    for s in ["todo", "in_progress", "in_review", "done"]:
        r = await db.execute(
            select(func.count(Task.id)).where(Task.project_id == project_id, Task.status == s, Task.is_deleted == False)
        )
        status_counts[s] = r.scalar() or 0

    now = datetime.now(timezone.utc)
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.status != "done",
            Task.is_deleted == False,
            Task.due_date < now,
        )
    )
    overdue = overdue_result.scalar() or 0

    priority_counts = {}
    for p in ["low", "medium", "high", "critical"]:
        r = await db.execute(
            select(func.count(Task.id)).where(Task.project_id == project_id, Task.priority == p, Task.is_deleted == False)
        )
        priority_counts[p] = r.scalar() or 0

    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_tasks": total_tasks,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "overdue": overdue,
        "progress": round((status_counts.get("done", 0) / total_tasks) * 100) if total_tasks > 0 else 0,
    }