from sqlalchemy import Column, String, Text, Integer
from app.db_pg import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True)
    os = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    mac = Column(String, nullable=True)          # ✅ Added previously
    hostname = Column(String, nullable=True)
    vendor = Column(String, nullable=True)       # ✅ Added previously
    username = Column(String, nullable=True)     # ✅ NEW: to store agent's username
    status = Column(String, nullable=True)

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
