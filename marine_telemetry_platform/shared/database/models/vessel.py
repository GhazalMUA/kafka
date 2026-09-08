from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import Base    
    
class Vessel(Base):
    __tablename__ = 'vessels' 
    
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key = True
    )
    
    name: Mapped[str | None] = mapped_column(
        String(200),
        nullable= True
    )   
    
    creates_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
        nullable= False,
        server_default=func.now()
    )