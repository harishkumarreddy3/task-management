from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from src.taskmanager.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_date = Column(DateTime, default=datetime.now(timezone.utc))