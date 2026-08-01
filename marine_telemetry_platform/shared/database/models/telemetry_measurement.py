from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import Base


class TelemetryMeasurement(Base):
    __tablename__ = "telemetry_measurements"

    __table_args__ = (
        Index(
            "ix_telemetry_measurements_equipment_measured_at",
            "equipment_id",
            "measured_at",
        ),
        Index(
            "ix_telemetry_measurements_sensor_measured_at",
            "sensor_id",
            "measured_at",
        ),
    )

    event_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )

    schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    vessel_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    equipment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sensor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    measurement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )