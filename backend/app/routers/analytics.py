from fastapi import APIRouter, Depends
from app.models.user import User
from app.services.task_service import get_dashboard_stats
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_stats(current_user: User = Depends(get_current_user)):
    from app.database import async_session
    async with async_session() as db:
        return await get_dashboard_stats(db, current_user.id)