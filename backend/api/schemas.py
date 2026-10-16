from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from api.enums import Category, Severity, IncidentStatus

class IncidentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: Category
    severity: Severity
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    location: str= Field(min_length=1, max_length=200)
    vehicle_id: str=Field(min_length=1, max_length=50)


class IncidentUpdate(BaseModel):
    model_config=ConfigDict(extra="forbid", str_strip_whitespace=True)

    expected_version: int = Field(ge=1)
    category: Category | None = None
    severity: Severity | None = None
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, min_length=1,max_length=2000)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    vehicle_id: str | None = Field(default=None, min_length=1, max_length=50)
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