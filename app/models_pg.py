# models_pg.py

from sqlalchemy import Column, String, Text, Integer, Enum
from app.db_pg import Base

class Agent(Base):
    __tablename__ = "agents"
    agent_id = Column(String, primary_key=True)
    os = Column(String)
    ip = Column(String)
    hostname = Column(String)
    status = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True)
    agent_id = Column(String)
    os_type = Column(String)
    command = Column(Text)
    status = Column(String, default="queued")
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    returncode = Column(Integer, nullable=True)
