from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.enums import Category, Severity, IncidentStatus

class IncidentCreate(BaseModel):
    category: Category
    severity: Severity
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    location: str= Field(min_length=1)
    vehicle_id: str=Field(min_length=1)


class IncidentUpdate(BaseModel):
    model_config=ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    category: Category | None = None
    severity: Severity | None = None
    title: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None)
    vehicle_id: str | None = Field(default=None)
    status: IncidentStatus | None = None

class IncidentResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    
    id: int
    category: Category
    severity: Severity
    status: IncidentStatus
    title: str
    description: str
    location: str
    vehicle_id: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime
    version: int