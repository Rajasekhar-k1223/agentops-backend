from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db_pg import Base

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True)
    os = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    mac = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    username = Column(String, nullable=True)
    status = Column(String, nullable=True)
    last_seen = Column(TIMESTAMP, nullable=True)

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
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)

class GeneratedTask(Base):
    __tablename__ = "generated_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_description = Column(Text, nullable=False)
    os_type = Column(String, nullable=False)
    generated_command = Column(Text, nullable=False)
    model_used = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class CommandList(Base):
    __tablename__ = "command_list"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_description = Column(Text, nullable=False)
    os_type = Column(String, nullable=False)
    final_command = Column(Text, nullable=False)
    approved_by = Column(String, nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    assigned_agent = Column(String, nullable=True)
    assigned_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, nullable=False)
    feedback = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(TIMESTAMP, server_default=func.now())
