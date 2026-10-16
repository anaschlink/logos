from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from api.config import settings

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 5}

engine = create_engine(settings.database_url, connect_args=connect_args)

@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    if settings.database_url.startswith("sqlite"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
