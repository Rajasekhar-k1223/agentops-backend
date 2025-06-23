# models.py - Pydantic Models for AgentOps System

from pydantic import BaseModel
from typing import Optional, List

# Request model for generating tasks
class TaskRequest(BaseModel):
    command: str
    os_type: Optional[str] = None
    agent_id: Optional[str] = None

# Model for returning task execution results
class TaskResult(BaseModel):
    agent_id: str
    task_id: str
    stdout: str
    stderr: str
    returncode: int
    status: str

# Agent registration or heartbeat info
class AgentInfo(BaseModel):
    agent_id: Optional[str] = None
    os: Optional[str] = None
    status: Optional[str] = "online"

# For summarizing log analysis
class LogAnalysisResult(BaseModel):
    category: str
    issues: List[str]
    suggestions: List[str]

# Task generation model supporting multiple agents
class TaskGenRequestMulti(BaseModel):
    command: str
    os_type: Optional[str] = None
    agent_ids: List[str]

# Admin approving a command
class ApproveCommandRequest(BaseModel):
    command_id: str
    approved_by: str

# Assigning a command to an agent
class AssignCommandRequest(BaseModel):
    command_id: str
    agent_id: str

# Feedback given by user
class FeedbackRequest(BaseModel):
    task_id: str
    feedback: str

# User model for JWT-based auth (used internally)
class UserLoginRequest(BaseModel):
    username: str
    password: str
