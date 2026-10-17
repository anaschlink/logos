from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

import api.models 
from api.config import settings
from api.database import Base, SessionLocal, engine, get_db
from api.errors import register_exception_handlers
from api.routers import incidents
from api.seed import seed_incidents

from pathlib import Path
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_incidents(db)
    yield


app = FastAPI(title="Logos API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-Analyst"],
)

register_exception_handlers(app)
app.include_router(incidents.router, prefix="/api")


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")) 
    return {"status": "ok"}

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="web")