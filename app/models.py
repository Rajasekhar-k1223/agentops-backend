# models.py - Pydantic Models for AgentOps System

from pydantic import BaseModel
from typing import Optional

class TaskRequest(BaseModel):
    command: str
    os_type: Optional[str] = None
    agent_id: Optional[str] = None

class TaskResult(BaseModel):
    agent_id: str
    task_id: str
    stdout: str
    stderr: str
    returncode: int
    status: str

class AgentInfo(BaseModel):
    agent_id: Optional[str] = None
    os: Optional[str] = None
    status: Optional[str] = "online"

class LogAnalysisResult(BaseModel):
    category: str
    issues: list[str]
    suggestions: list[str]
