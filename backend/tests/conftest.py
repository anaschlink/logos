import os
import tempfile

# Precisa vir ANTES de qualquer import de api.*: o settings é lido no import.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"

import pytest
from fastapi.testclient import TestClient

from api.database import Base, engine
from api.main import app

ANA = {"X-Analyst": "Ana Silva"}
CARLOS = {"X-Analyst": "Carlos Souza"}

PAYLOAD = {
    "category": "Bloqueio de Pista",
    "severity": "Alta",
    "title": "Teste",
    "description": "Descrição de teste",
    "location": "BR-116, km 10, SP",
    "vehicle_id": "FIC-0001",
}


@pytest.fixture()
def client():
    # Sem `with`: o lifespan não roda, então não há seed. Cada teste começa com banco vazio.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return TestClient(app)


@pytest.fixture()
def make(client):
    def _make(**overrides):
        r = client.post("/api/incidents", json={**PAYLOAD, **overrides})
        assert r.status_code == 201, r.text
        return r.json()
    return _make