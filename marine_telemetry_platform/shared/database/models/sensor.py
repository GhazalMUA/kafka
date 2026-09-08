
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index,String,func

from sqlalchemy.orm import Mapped, mapped_column    
from shared.database.base import Base

class Sensor(Base):
    __tablename__ = 'sensors'
    
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key= True
    )
    
    equipment_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("equipment.id"),
        nullable= False
    )
    
    measurement_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable = False
    )
    
    created_at: Mapped[datetime]= mapped_column(
        DateTime(timezone=True),
        nullable= False,
        server_default= func.now()
    )
    
    __table_args__ = (
        Index(
            "ix_sensors_equipment_id",
            "equipemnt_id"
        )
    )