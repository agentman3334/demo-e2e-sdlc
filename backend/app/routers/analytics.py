from fastapi import APIRouter, Depends
from app.models.user import User
from app.services.task_service import get_dashboard_stats, get_project_stats
from app.services.project_service import is_project_member
from app.utils.dependencies import get_current_user
from fastapi import HTTPException

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_stats(current_user: User = Depends(get_current_user)):
    from app.database import async_session
    async with async_session() as db:
        return await get_dashboard_stats(db, current_user.id)


@router.get(
    "/project/{project_id}",
    responses={403: {"description": "Not a project member"}, 404: {"description": "Project not found"}},
)
async def project_stats(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    from app.database import async_session
    async with async_session() as db:
        if not await is_project_member(db, project_id, current_user.id) and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not a project member")
        return await get_project_stats(db, project_id)