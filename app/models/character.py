from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    occupation_id = Column(Integer, ForeignKey("occupations.id"))
    profile_image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    introduction = Column(Text)
    prefecture_id = Column(Integer, ForeignKey("prefectures.id"))
    municipality_id = Column(Integer, ForeignKey("municipalities.id"))
    tasuki_project_id = Column(Integer)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    occupation = relationship("Occupation", back_populates="characters")
    prefecture = relationship("Prefecture", back_populates="characters")
    municipality = relationship("Municipality", back_populates="characters")
    relationships = relationship("Relationship", back_populates="character")