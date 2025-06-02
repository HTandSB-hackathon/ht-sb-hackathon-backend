from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    occupation_id = Column(Integer, ForeignKey("occupations.id"))
    profile_image_url = Column(String(500))
    cover_image_url = Column(String(500))
    gender = Column(Integer, nullable=False)  # 0: 男性, 1: 女性, 2: その他
    personality = Column(ARRAY(String), default=list)  # Personality traits as an array of strings
    hobbies = Column(ARRAY(String), default=list)  # Hobbies as an array of strings
    specialties = Column(ARRAY(String), default=list)  # Specialties as an array of strings
    is_active = Column(Boolean, default=True)
    introduction = Column(Text)
    unlock_condition = Column(Text, nullable=True, default="このキャラクターは現在取得できません")  # Unlock condition for the character
    prefecture_id = Column(Integer, ForeignKey("prefectures.id"))
    municipality_id = Column(Integer, ForeignKey("municipalities.id"))
    tasuki_project_id = Column(Integer)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # occupation = relationship("Occupation", back_populates="characters")
    # prefecture = relationship("Prefecture", back_populates="characters")
    # municipality = relationship("Municipality", back_populates="characters")
    # relationships = relationship("Relationship", back_populates="character")


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    required_trust_level = Column(Integer, nullable=False, default=0)  # Trust level required to unlock the story
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # character = relationship("Character", back_populates="stories")