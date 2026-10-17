from datetime import datetime
from api.enums import Category, Severity, IncidentStatus
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
from api.transitions import allowed_targets

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

    @model_validator(mode="after")
    def _validate_sent_fields(self):
        sent = self.model_fields_set - {"expected_version"}
        if not sent:
            raise ValueError("Informe ao menos um campo para alterar.")
        nulls = sorted(f for f in sent if getattr(self, f) is None)
        if nulls:
            raise ValueError(f"Campos não aceitam null: {', '.join(nulls)}.")
        return self

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

    @computed_field
    @property
    def allowed_transitions(self) -> list[IncidentStatus]:
        return allowed_targets(self.status)


class SummaryResponse(BaseModel):
    total: int
    by_severity: dict[Severity, int]