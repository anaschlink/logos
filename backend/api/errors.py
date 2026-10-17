import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("logos")


class DomainError(Exception):
    status_code = 400
    code = "domain_error"

    def __init__(self, message: str, *, details: Any = None, current: Any = None,
                 headers: dict[str, str] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details
        self.current = current
        self.headers = headers


class NotFoundError(DomainError):
    status_code, code = 404, "not_found"


class VersionConflictError(DomainError):
    status_code, code = 409, "version_conflict"


class InvalidTransitionError(DomainError):
    status_code, code = 422, "invalid_transition"


class NotAssigneeError(DomainError):
    status_code, code = 403, "not_assignee"


class MissingAnalystError(DomainError):
    status_code, code = 422, "missing_analyst"


def _body(code: str, message: str, details: Any = None, current: Any = None) -> dict:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    if current is not None:
        error["current"] = jsonable_encoder(current)
    return {"error": error}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content=_body(exc.code, exc.message, exc.details, exc.current),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [
            {
                "field": ".".join(str(p) for p in e["loc"][1:]),
                "message": e["msg"].removeprefix("Value error, "),
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_body("validation_error", "Dados inválidos.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        codes = {404: "not_found", 405: "method_not_allowed"}
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(codes.get(exc.status_code, "http_error"), str(exc.detail)),
        )

    @app.exception_handler(OperationalError)
    async def db_handler(request: Request, exc: OperationalError):
        logger.warning("Banco indisponível: %s", exc)
        return JSONResponse(
            status_code=503,
            headers={"Retry-After": "2"},
            content=_body(
                "database_unavailable",
                "Banco de dados temporariamente indisponível. Tente novamente.",
            ),
        )

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        logger.exception("Erro inesperado")
        return JSONResponse(
            status_code=500,
            content=_body("internal_error", "Erro interno do servidor."),
        )