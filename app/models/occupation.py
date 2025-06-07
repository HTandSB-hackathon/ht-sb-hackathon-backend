from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Occupation(Base):
    __tablename__ = "occupations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # characters = relationship("Character", back_populates="occupation")