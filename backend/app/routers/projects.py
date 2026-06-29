from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberAdd, ProjectMemberResponse
from app.services.project_service import (
    create_project, get_project, list_projects, update_project,
    soft_delete_project, add_member, remove_member, is_project_member,
)
from app.utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectResponse])
async def list_user_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_projects(db, current_user.id)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    project = await create_project(db, project_in, current_user.id)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_detail(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not await is_project_member(db, project_id, current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not a project member")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_detail(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    return await update_project(db, project, project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(require_role("admin",)),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    await soft_delete_project(db, project)


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: str,
    member_in: ProjectMemberAdd,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    await get_project(db, project_id)
    return await add_member(db, project_id, member_in.user_id, member_in.role)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(require_role("admin", "project_manager")),
    db: AsyncSession = Depends(get_db),
):
    await get_project(db, project_id)
    await remove_member(db, project_id, user_id)