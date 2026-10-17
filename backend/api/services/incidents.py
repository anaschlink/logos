from datetime import datetime, timezone
from typing import NoReturn

from sqlalchemy import case, delete, func, or_, select, update
from sqlalchemy.orm import Session

from api.enums import Category, IncidentStatus, Severity
from api.errors import NotFoundError, VersionConflictError
from api.models import Incident
from api.schemas import IncidentCreate, IncidentResponse, IncidentUpdate
from api.transitions import status_change_effects

# ORDER BY direto na coluna seria alfabético (Alta, Baixa, Média).
SEVERITY_RANK = case(
    (Incident.severity == Severity.HIGH, 0),
    (Incident.severity == Severity.MEDIUM, 1),
    else_=2,
)


def list_incidents(
    db: Session,
    *,
    severities: list[Severity] | None,
    categories: list[Category] | None,
    statuses: list[IncidentStatus] | None,
    q: str | None,
) -> list[Incident]:
    stmt = select(Incident)
    if severities:
        stmt = stmt.where(Incident.severity.in_(severities))
    if categories:
        stmt = stmt.where(Incident.category.in_(categories))
    if statuses:
        stmt = stmt.where(Incident.status.in_(statuses))
    else:
        stmt = stmt.where(Incident.status != IncidentStatus.CLOSED)
    if q and q.strip():
        term = q.strip()
        stmt = stmt.where(or_(
            Incident.title.icontains(term, autoescape=True),
            Incident.location.icontains(term, autoescape=True),
            Incident.vehicle_id.icontains(term, autoescape=True),
        ))
    return list(db.scalars(
        stmt.order_by(SEVERITY_RANK, Incident.created_at.asc(), Incident.id.asc())
    ))


def summarize(db: Session) -> dict:
    rows = db.execute(
        select(Incident.severity, func.count())
        .where(Incident.status != IncidentStatus.CLOSED)
        .group_by(Incident.severity)
    ).all()
    by_severity = {s: 0 for s in Severity}
    by_severity.update(dict(rows))
    return {"total": sum(by_severity.values()), "by_severity": by_severity}


def get_incident(db: Session, incident_id: int) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise NotFoundError(f"Incidente {incident_id} não encontrado.")
    return incident


def create_incident(db: Session, payload: IncidentCreate) -> Incident:
    incident = Incident(
        **payload.model_dump(), status=IncidentStatus.OPEN, assigned_to=None, version=1
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def _raise_stale(db: Session, incident_id: int) -> NoReturn:
    """Versão desatualizada ou 0 linhas afetadas: 404 se sumiu, 409 se mudou."""
    db.rollback()
    db.expire_all()
    fresh = db.get(Incident, incident_id)
    if fresh is None:
        raise NotFoundError(f"Incidente {incident_id} não encontrado.")
    raise VersionConflictError(
        "O incidente foi alterado por outro analista. Revise o estado atual.",
        current=IncidentResponse.model_validate(fresh),
    )


def update_incident(
    db: Session, incident_id: int, payload: IncidentUpdate, analyst: str
) -> Incident:
    incident = get_incident(db, incident_id)

    # cliente desatualizado recebe 409, nunca um 422 sobre estado que ele não vê.
    if incident.version != payload.expected_version:
        _raise_stale(db, incident_id)

    values = payload.model_dump(exclude_unset=True, exclude={"expected_version"})
    if "status" in values:
        values.update(status_change_effects(
            incident.status, incident.assigned_to, values["status"], analyst
        ))

    # WHERE version fecha a janela entre o SELECT e o UPDATE.
    result = db.execute(
        update(Incident)
        .where(Incident.id == incident_id, Incident.version == payload.expected_version)
        .values(**values, version=Incident.version + 1, updated_at=datetime.now(timezone.utc))
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        _raise_stale(db, incident_id)

    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident_id: int, expected_version: int) -> None:
    result = db.execute(
        delete(Incident)
        .where(Incident.id == incident_id, Incident.version == expected_version)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        _raise_stale(db, incident_id)
    db.commit()