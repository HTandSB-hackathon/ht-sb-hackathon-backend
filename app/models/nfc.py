from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base_class import Base


class UserNfcUuid(Base):
    __tablename__ = "user_nfc_uuids"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nfc_uuid = Column(String, nullable=False, index=True, unique=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
