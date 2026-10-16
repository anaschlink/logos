from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator
from api.database import Base
from api.enums import Category, Severity, IncidentStatus

class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.astimezone(timezone.utc).replace(tzinfo=None)if value else value

    def process_result_value(self, value, dialect):
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value else value


class Incident(Base):
    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    category: Mapped[Category] = mapped_column(
        SAEnum(Category, 
                name="incident_category",
                native_enum=False,
                values_callable=lambda e: [m.value for m in e]),
        nullable=False, 
    )

    severity: Mapped[Severity] = mapped_column(
        SAEnum(Severity, 
                name="incident_severity",
                native_enum=False,
                values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, 
               name="incident_status",                  native_enum=False,
               values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    vehicle_id: Mapped[str] = mapped_column(String, nullable=False)

    assigned_to: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )

