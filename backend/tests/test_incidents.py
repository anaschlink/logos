from tests.conftest import ANA, CARLOS, PAYLOAD

def patch(client, incident, headers=ANA, **fields):
    return client.patch(
        f"/api/incidents/{incident['id']}",
        json={"expected_version": incident["version"], **fields},
        headers=headers,
    )


def code(response):
    return response.json()["error"]["code"]


# 1. Conflito de versão (pergunta 3 do case)
def test_version_conflict_returns_409_with_current_state(client, make):
    incident = make()

    first = patch(client, incident, status="Em Investigação")
    assert first.status_code == 200
    assert first.json()["version"] == 2

    second = patch(client, incident, status="Em Investigação")  # ainda com version 1
    assert second.status_code == 409
    assert code(second) == "version_conflict"
    assert second.json()["error"]["current"]["version"] == 2


# 2. Transição inválida
def test_invalid_transition_returns_422(client, make):
    incident = make()
    investigating = patch(client, incident, status="Em Investigação").json()
    closed = patch(client, investigating, status="Fechado").json()

    reopen = patch(client, closed, status="Aberto")  # Fechado é terminal
    assert reopen.status_code == 422
    assert code(reopen) == "invalid_transition"


# 3. Filtros e ordenação
def test_filters_and_ordering(client, make):
    make(severity="Baixa", title="baixa")
    first_high = make(severity="Alta", title="alta 1")
    make(severity="Média", title="media")
    second_high = make(severity="Alta", title="alta 2")

    listed = client.get("/api/incidents").json()
    assert [i["severity"] for i in listed] == ["Alta", "Alta", "Média", "Baixa"]
    assert [i["id"] for i in listed[:2]] == [first_high["id"], second_high["id"]]

    only_high = client.get("/api/incidents", params={"severity": "Alta"}).json()
    assert len(only_high) == 2

    combined = client.get(
        "/api/incidents", params={"severity": ["Alta", "Baixa"], "q": "alta"}
    ).json()
    assert len(combined) == 2


def test_closed_hidden_by_default(client, make):
    incident = make()
    investigating = patch(client, incident, status="Em Investigação").json()
    patch(client, investigating, status="Fechado")

    assert client.get("/api/incidents").json() == []
    closed = client.get("/api/incidents", params={"status": "Fechado"}).json()
    assert len(closed) == 1


# 4. Validação
def test_validation_errors(client, make):
    bad_category = client.post("/api/incidents", json={**PAYLOAD, "category": "Inexistente"})
    assert bad_category.status_code == 422
    assert code(bad_category) == "validation_error"

    too_long = client.post("/api/incidents", json={**PAYLOAD, "title": "x" * 121})
    assert too_long.status_code == 422

    extra_field = client.post("/api/incidents", json={**PAYLOAD, "status": "Fechado"})
    assert extra_field.status_code == 422

    incident = make()
    null_title = patch(client, incident, title=None)
    assert null_title.status_code == 422

    nothing_to_change = client.patch(
        f"/api/incidents/{incident['id']}",
        json={"expected_version": 1},
        headers=ANA,
    )
    assert nothing_to_change.status_code == 422


# 5. 404 e cabeçalho obrigatório
def test_patch_missing_incident_returns_404(client):
    r = client.patch(
        "/api/incidents/9999",
        json={"expected_version": 1, "title": "x"},
        headers=ANA,
    )
    assert r.status_code == 404
    assert code(r) == "not_found"


def test_patch_without_analyst_header_returns_422(client, make):
    incident = make()
    r = client.patch(
        f"/api/incidents/{incident['id']}",
        json={"expected_version": 1, "title": "x"},
    )
    assert r.status_code == 422
    assert code(r) == "missing_analyst"


# 6. Só o responsável encerra
def test_only_assignee_can_close(client, make):
    incident = make()
    claimed = patch(client, incident, status="Em Investigação").json()
    assert claimed["assigned_to"] == "Ana Silva"

    by_carlos = patch(client, claimed, headers=CARLOS, status="Fechado")
    assert by_carlos.status_code == 403
    assert code(by_carlos) == "not_assignee"

    by_ana = patch(client, claimed, status="Fechado")
    assert by_ana.status_code == 200
    assert by_ana.json()["status"] == "Fechado"