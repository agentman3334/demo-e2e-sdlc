from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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