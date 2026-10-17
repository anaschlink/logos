import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.enums import Category, Severity, IncidentStatus
from api.models import Incident

SEED = 123
TOTAL_INCIDENTS=100

CATEGORIES = [
    Category.VEHICLE_ACCIDENT,
    Category.ACCIDENT_WITH_VICTIMS,
    Category.ABNORMAL_WEATHER,
    Category.MECHANICAL_FAILURE,
    Category.ROAD_BLOCKAGE
]

SEVERITIES = (
    [Severity.HIGH]*10
    +[Severity.MEDIUM]*30
    +[Severity.LOW]*60
)

ANALYSTS = [
    "Ana Silva",
    "Carlos Souza",
    "Mariana Costa",
    "Pedro Oliveira"
]

ROADS = [
    ("BR-116", "SP"),
    ("BR-101", "RJ"),
    ("SP-330", "SP"),
    ("BR-381", "MG"),
    ("BR-040", "MG"),
    ("BR-153", "GO"),
]

INCIDENT_DETAILS = {
    Category.VEHICLE_ACCIDENT: (
        "Acidente com veículo",
        "Colisão envolvendo veículo na rodovia.",
    ),
    Category.ACCIDENT_WITH_VICTIMS: (
        "Acidente com vítimas",
        "Ocorrência com vítimas que exige avaliação da equipe.",
    ),
    Category.ABNORMAL_WEATHER: (
        "Condição climática atípica",
        "Condições climáticas adversas afetam a segurança da pista.",
    ),
    Category.MECHANICAL_FAILURE: (
        "Problema mecânico",
        "Veículo apresenta falha mecânica e pode obstruir a via.",
    ),
    Category.ROAD_BLOCKAGE: (
        "Bloqueio de pista",
        "Trecho da rodovia apresenta bloqueio parcial ou total.",
    ),
}

def seed_incidents(db:Session) -> int:
    "Insere 100 incidents se a tabela estiver vazia"

    if db.query(Incident).first() is not None:
        return 0

    rng = random.Random(SEED)
    now = datetime.now(timezone.utc)

    severities = list(SEVERITIES)
    rng.shuffle(severities)

    incidents = []

    for i in range(TOTAL_INCIDENTS):
        category = rng.choice(CATEGORIES)
        severity = severities[i]

        title , description = INCIDENT_DETAILS[category]

        road, state = rng.choice(ROADS)
        km = rng.randint(1,900)
        location = f"{road}, km {km}, {state}"

        vehicle_id = (
            f"FIC-{rng.randint(1000, 9999)}"
        )

        age_minutes = rng.randint(1, 12 * 60)
        created_at = now - timedelta(minutes=age_minutes)

        status_roll = rng.random()

        if status_roll < 0.20:
            status = IncidentStatus.INVESTIGATING
            assigned_to = rng.choice(ANALYSTS)
        elif status_roll < 0.30:
            status = IncidentStatus.CLOSED
            assigned_to = rng.choice(ANALYSTS)
        elif status_roll < 0.35:
            status = IncidentStatus.INCONCLUSIVE
            assigned_to = None
        else:
            status = IncidentStatus.OPEN
            assigned_to = None

        incidents.append(
            Incident(
                category = category,
                severity = severity,
                status = status,
                title=f"{title} #{i + 1:03d}",
                description=description,
                location=location,
                vehicle_id=vehicle_id,
                assigned_to=assigned_to,
                created_at=created_at,
                updated_at=created_at,
                version= 1
            )
        )

    try:
        db.add_all(incidents)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return len(incidents)


def main() -> None:
    db=SessionLocal()

    try:
        inserted = seed_incidents(db)

        if inserted:
            print(f"Seed concluído: {inserted} incidents inseridos")
        else:
            print("Seed ignorado: a tabela já contém incidents")
    finally:
        db.close()

if __name__ == "__main__":
    main()