from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks_advanced"  # ← changed from "tasks"

    id         = Column(Integer, primary_key=True, index=True)
    goal       = Column(String)
    subtask    = Column(Text)
    status     = Column(String)
    result     = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)