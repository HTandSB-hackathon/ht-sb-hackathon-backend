from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Prefecture(Base):
    __tablename__ = "prefectures"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    municipalities = relationship("Municipality", back_populates="prefecture")
    # characters = relationship("Character", back_populates="prefecture")

class Municipality(Base):
    __tablename__ = "municipalities"
    
    id = Column(Integer, primary_key=True, index=True)
    prefecture_id = Column(Integer, ForeignKey("prefectures.id"), nullable=False)
    name = Column(String(50), nullable=False)
    kana = Column(String(50))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prefecture = relationship("Prefecture", back_populates="municipalities")
    # characters = relationship("Character", back_populates="municipality")