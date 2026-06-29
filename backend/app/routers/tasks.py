from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, PaginatedTaskResponse
from app.services.task_service import create_task, get_task, list_tasks, update_task, update_task_status, delete_task
from app.services.project_service import get_project, is_project_member
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=PaginatedTaskResponse)
async def list_all_tasks(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_tasks(db, project_id, status, page, size)


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    project_id: str,
    task_in: TaskCreate,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    await get_project(db, project_id)
    return await create_task(db, project_id, task_in)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_task(db, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={403: {"description": "Can only update your own tasks"}, 404: {"description": "Task not found"}},
)
async def update_task_detail(
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task(db, task_id)
    if current_user.role == "member" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
    return await update_task(db, task, task_in)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    responses={403: {"description": "Can only update your own tasks"}, 404: {"description": "Task not found"}},
)
async def update_task_status_endpoint(
    task_id: str,
    status_in: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task(db, task_id)
    if current_user.role == "member" and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own tasks")
    return await update_task_status(db, task, status_in.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: str,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task(db, task_id)
    await delete_task(db, task)