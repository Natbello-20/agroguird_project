from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class AEO(Base):
    __tablename__ = "aeo"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String, unique=True, nullable=False)
    ghana_card = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    must_change_password = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
