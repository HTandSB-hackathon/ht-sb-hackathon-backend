from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base_class import Base


class TrustLevel(Base):
    __tablename__ = "trust_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # relationships = relationship("Relationship", back_populates="trust_level")

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    trust_level_id = Column(Integer, ForeignKey("trust_levels.id"), nullable=False)
    total_points = Column(Integer, default=0)
    conversation_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    first_met_at = Column(DateTime(timezone=True))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # user = relationship("Users", back_populates="relationships")
    # character = relationship("Character", back_populates="relationships")
    # trust_level = relationship("TrustLevel", back_populates="relationships")

class LevelThreshold(Base):
    __tablename__ = "level_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    trust_level_id = Column(Integer, ForeignKey("trust_levels.id"), nullable=False)
    required_points = Column(Integer, default=0)
    required_conversations = Column(Integer, default=0)
    required_days_from_first = Column(Integer, default=0)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())