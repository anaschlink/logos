from api.enums import IncidentStatus as S
from api.errors import InvalidTransitionError, NotAssigneeError

ALLOWED: dict[S, set[S]] = {
    S.OPEN: {S.INVESTIGATING},
    S.INVESTIGATING: {S.CLOSED, S.INCONCLUSIVE, S.OPEN},
    S.INCONCLUSIVE: {S.INVESTIGATING},
    S.CLOSED: set(),
}

_ORDER = list(S)


def can_transition(current: S, target: S) -> bool:
    return target in ALLOWED[current]


def allowed_targets(current: S) -> list[S]:
    return [s for s in _ORDER if s in ALLOWED[current]]


def status_change_effects(
    current: S, assigned_to: str | None, target: S, analyst: str
) -> dict:
    """Valida a mudança de status e devolve os campos a gravar (status + responsável)."""
    if not can_transition(current, target):
        raise InvalidTransitionError(
            f"Transição de '{current.value}' para '{target.value}' não é permitida."
        )
    if current == S.INVESTIGATING and assigned_to != analyst:
        raise NotAssigneeError(
            f"Este incidente está com {assigned_to}. "
            "Só o responsável pode encerrá-lo ou devolvê-lo à fila."
        )
    effects: dict = {"status": target}
    if target == S.INVESTIGATING:
        effects["assigned_to"] = analyst 
    elif target == S.OPEN:
        effects["assigned_to"] = None  
    return effects