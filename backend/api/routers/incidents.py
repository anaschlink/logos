from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session

from api.database import get_db
from api.enums import Category, IncidentStatus, Severity
from api.errors import MissingAnalystError
from api.schemas import (
    IncidentCreate, IncidentResponse, IncidentUpdate, SummaryResponse,
)
from api.services import incidents as service

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_analyst(x_analyst: Annotated[str | None, Header()] = None) -> str:
    name = (x_analyst or "").strip()
    if not name or len(name) > 100:
        raise MissingAnalystError("Cabeçalho X-Analyst é obrigatório (máx. 100 caracteres).")
    return name


@router.get("", response_model=list[IncidentResponse])
def list_incidents(
    db: Annotated[Session, Depends(get_db)],
    severity: Annotated[list[Severity] | None, Query()] = None,
    category: Annotated[list[Category] | None, Query()] = None,
    status: Annotated[list[IncidentStatus] | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
):
    return service.list_incidents(
        db, severities=severity, categories=category,
        statuses=status, q=q,
    )


# Declarada antes de /{incident_id}, senão "summary" seria lido como id.
@router.get("/summary", response_model=SummaryResponse)
def summary(db: Annotated[Session, Depends(get_db)]):
    return service.summarize(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Annotated[Session, Depends(get_db)]):
    return service.get_incident(db, incident_id)


@router.post("", response_model=IncidentResponse, status_code=201)
def create_incident(payload: IncidentCreate, db: Annotated[Session, Depends(get_db)]):
    return service.create_incident(db, payload)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Annotated[Session, Depends(get_db)],
    analyst: Annotated[str, Depends(get_analyst)],
):
    return service.update_incident(db, incident_id, payload, analyst)


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: int,
    expected_version: Annotated[int, Query(ge=1)],
    db: Annotated[Session, Depends(get_db)],
):
    service.delete_incident(db, incident_id, expected_version)
    return Response(status_code=204)