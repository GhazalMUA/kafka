
    
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index,String,func

from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import Base

class Equipment(Base): 
    __tablename__ = 'equipment'  
    
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key= True
    )
           
    vessle_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("vessel.id"),
        nullable=False
    )    
    
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    __table_args__ = (
        Index(
            "ix_equipment_vessel_id",
            "vessel_id"
            ),
    )