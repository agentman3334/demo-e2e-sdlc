from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException


async def get_or_404(db: AsyncSession, model, entity_id: str, name: str = "Entity"):
    result = await db.execute(select(model).where(model.id == entity_id, model.is_deleted == False))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return entity


async def apply_update(db: AsyncSession, entity, update_schema):
    update_data = update_schema.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)
    await db.flush()
    return entity


async def soft_delete(db: AsyncSession, entity):
    entity.is_deleted = True
    await db.flush()
    return entity


async def paginated_list(db: AsyncSession, base_query, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar() or 0
    result = await db.execute(base_query.offset(offset).limit(size))
    items = list(result.scalars().all())
    return {"items": items, "total": total, "page": page, "size": size}