from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    vessel_id: Mapped[str] = mapped_column(String(100), ForeignKey("vessels.id"), nullable=False)

    name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "vessel_id",
            "id",
            name="uq_equipment_vessel_id_id",
        ),
        Index(
            "ix_equipment_vessel_id",
            "vessel_id",
        ),
    )
