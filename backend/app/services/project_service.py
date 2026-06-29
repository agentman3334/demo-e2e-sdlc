from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from fastapi import HTTPException, status


async def create_project(db: AsyncSession, project_in: ProjectCreate, owner_id: str) -> Project:
    project = Project(
        name=project_in.name,
        description=project_in.description,
        deadline=project_in.deadline,
        owner_id=owner_id,
    )
    db.add(project)
    await db.flush()
    member = ProjectMember(project_id=project.id, user_id=owner_id, role="project_manager")
    db.add(member)
    await db.flush()
    return project


async def get_project(db: AsyncSession, project_id: str) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id, Project.is_deleted == False))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def list_projects(db: AsyncSession, user_id: str, page: int = 1, size: int = 20) -> dict:
    offset = (page - 1) * size
    base_query = (
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user_id, Project.is_deleted == False)
    )
    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = count_result.scalar() or 0
    result = await db.execute(
        base_query.order_by(Project.created_at.desc()).offset(offset).limit(size)
    )
    items = list(result.scalars().all())
    return {"items": items, "total": total, "page": page, "size": size}


async def update_project(db: AsyncSession, project: Project, project_in: ProjectUpdate) -> Project:
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.flush()
    return project


async def soft_delete_project(db: AsyncSession, project: Project) -> Project:
    project.is_deleted = True
    await db.flush()
    return project


async def add_member(db: AsyncSession, project_id: str, user_id: str, role: str = "member") -> ProjectMember:
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
    db.add(member)
    await db.flush()
    return member


async def remove_member(db: AsyncSession, project_id: str, user_id: str) -> None:
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in project")
    await db.delete(member)
    await db.flush()


async def is_project_member(db: AsyncSession, project_id: str, user_id: str) -> bool:
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None