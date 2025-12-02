from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone
from src.taskmanager.database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, index=True)
    desciption = Column(String, nullable=True)
    category = Column(String, index=True)  # work, personal, shopping
    priority = Column(String, index=True)  # low, medium, high
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.now(timezone.utc)) 