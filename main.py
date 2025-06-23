# # main.py - FastAPI Backend with PostgreSQL and MongoDB

# from fastapi import FastAPI, Request, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from app.models import TaskRequest, TaskResult, AgentInfo
# from app.db_pg import get_db, init_pg_db
# from app.db_mongo import insert_log, get_logs_by_task
# from app.models_pg import Agent, Task, GeneratedTask, CommandList
# from app.network_scanner import scan_network
# from app.genai_utils import generate_command
# import uuid
# import platform
# import socket
# import requests
# from pydantic import BaseModel
# from typing import List
# from datetime import datetime
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse
# from bson import ObjectId 
# from fastapi import FastAPI, Request, HTTPException, Depends, status
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from app.models import TaskRequest, TaskResult, AgentInfo, FeedbackRequest
# from app.db_pg import get_db, init_pg_db
# from app.db_mongo import insert_log, get_logs_by_task
# from app.models_pg import Agent, Task, GeneratedTask, CommandList, Feedback
# from app.network_scanner import scan_network
# from app.genai_utils import generate_command, summarize_logs, suggest_command
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# import uuid
# import platform
# import socket
# import requests
# from pydantic import BaseModel
# from typing import List
# from datetime import datetime, timedelta
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse
# from bson import ObjectId
# import logging



# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize PostgreSQL
# init_pg_db()


# # ========= Utility Functions =========

# def get_mac_vendor(mac: str) -> str:
#     try:
#         response = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
#         if response.status_code == 200:
#             return response.text
#     except Exception as e:
#         print(f"MAC vendor lookup failed for {mac}: {e}")
#     return "unknown"


# # ========= API Routes =========

# @app.post("/register-agent")
# def register_agent(agent: AgentInfo, db: Session = Depends(get_db)):
#     db_agent = db.query(Agent).filter(Agent.agent_id == agent.agent_id).first()
#     if not db_agent:
#         new_agent = Agent(
#             agent_id=agent.agent_id or str(uuid.uuid4()),
#             os=agent.os or platform.system(),
#             status=agent.status
#         )
#         db.add(new_agent)
#         db.commit()
#         return {"agent_id": new_agent.agent_id, "status": "registered"}
#     return {"agent_id": db_agent.agent_id, "status": "already-registered"}


# @app.get("/agents")
# def list_agents(db: Session = Depends(get_db)):
#     return db.query(Agent).all()


# @app.post("/submit-task")
# def submit_task(task: TaskRequest, db: Session = Depends(get_db)):
#     task_id = str(uuid.uuid4())
#     new_task = Task(
#         task_id=task_id,
#         command=task.command,
#         os_type=task.os_type,
#         agent_id=task.agent_id
#     )
#     db.add(new_task)
#     db.commit()
#     return {"status": "queued", "task_id": task_id}


# @app.get("/get-task/{agent_id}")
# def get_task(agent_id: str, db: Session = Depends(get_db)):
#     task = db.query(Task).filter(Task.agent_id == agent_id, Task.status == "queued").first()
#     if task:
#         task.status = "in_progress"
#         db.commit()
#         return {
#             "task_id": task.task_id,
#             "command": task.command,
#             "os_type": task.os_type
#         }
#     return {"message": "no-task"}


# @app.post("/return-task")
# def return_task(result: TaskResult, db: Session = Depends(get_db)):
#     task = db.query(Task).filter(Task.task_id == result.task_id).first()
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")

#     task.status = result.status
#     task.stdout = result.stdout
#     task.stderr = result.stderr
#     task.returncode = result.returncode
#     db.commit()

#     insert_log(result.task_id, result.dict())

#     return {"status": "result-stored"}


# # @app.get("/task-result/{task_id}")
# # def get_result(task_id: str, db: Session = Depends(get_db)):
# #     task = db.query(Task).filter(Task.task_id == task_id).first()
# #     if task:
# #         logs = get_logs_by_task(task_id)
# #         return {"task": task, "logs": logs}
# #     return {"status": "not-found"}

# def convert_objectid_to_str(doc):
#     """Convert MongoDB ObjectId and nested ObjectId fields to strings."""
#     if isinstance(doc, list):
#         return [convert_objectid_to_str(item) for item in doc]
#     if isinstance(doc, dict):
#         return {
#             key: str(value) if isinstance(value, ObjectId) else convert_objectid_to_str(value)
#             for key, value in doc.items()
#         }
#     return doc

# @app.get("/task-result/{task_id}")
# def get_result(task_id: str, db: Session = Depends(get_db)):
#     try:
#         task = db.query(Task).filter(Task.task_id == task_id).first()
#         if not task:
#             return JSONResponse(status_code=404, content={"error": "Task not found"})

#         logs = get_logs_by_task(task_id)
#         logs = convert_objectid_to_str(logs) if logs else []

#         return {
#             "task": jsonable_encoder(task),
#             "logs": logs
#         }
#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={"error": "Internal Server Error", "detail": str(e)}
#         )

# @app.get("/agents/network-scan")
# def agents_network_scan(db: Session = Depends(get_db)):
#     registered_agents = db.query(Agent).all()
#     registered_ips = {agent.ip: agent.agent_id for agent in registered_agents if agent.ip}

#     scanned_devices = scan_network("192.168.1.0/24")  # Adjust subnet as needed
#     response = []

#     for device in scanned_devices:
#         ip = device.get("ip")
#         mac = device.get("mac")
#         hostname = device.get("hostname", "unknown")
#         vendor = device.get("vendor", get_mac_vendor(mac))
#         os_type = device.get("os", "unknown")

#         agent_id = registered_ips.get(ip)

#         if agent_id:
#             existing_agent = db.query(Agent).filter(Agent.ip == ip).first()
#             existing_agent.mac = mac
#             existing_agent.hostname = hostname
#             existing_agent.vendor = vendor
#             existing_agent.os = os_type
#             db.commit()
#             status = "updated"
#         else:
#             new_agent = Agent(
#                 agent_id=str(uuid.uuid4()),
#                 ip=ip,
#                 mac=mac,
#                 hostname=hostname,
#                 vendor=vendor,
#                 os=os_type,
#                 status="unregistered"
#             )
#             db.add(new_agent)
#             db.commit()
#             agent_id = new_agent.agent_id
#             status = "registered"

#         response.append({
#             "ip": ip,
#             "mac": mac,
#             "hostname": hostname,
#             "vendor": vendor,
#             "os": os_type,
#             "agent_id": agent_id,
#             "status": status
#         })

#     return response


# class TaskGenRequestMulti(BaseModel):
#     task_description: str
#     os_list: List[str]
#     created_by: str = "system"
#     model_used: str = "ollama"


# @app.post("/generate-task")
# def generate_task(req: TaskGenRequestMulti, db: Session = Depends(get_db)):
#     generated_tasks = []

#     for os_type in req.os_list:
#         command = generate_command(req.task_description, os_type)

#         task_entry = GeneratedTask(
#             id=uuid.uuid4(),
#             task_description=req.task_description,
#             os_type=os_type,
#             generated_command=command,
#             model_used=req.model_used,
#             created_by=req.created_by,
#             created_at=datetime.utcnow()
#         )

#         db.add(task_entry)
#         generated_tasks.append({
#             "generated_task_id": str(task_entry.id),
#             "os": os_type,
#             "generated_command": command
#         })

#     try:
#         db.commit()
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"DB commit failed: {str(e)}")

#     return {
#         "description": req.task_description,
#         "generated_tasks": generated_tasks
#     }


# class ApproveCommandRequest(BaseModel):
#     generated_task_id: str
#     task_description: str
#     os_type: str
#     final_command: str
#     approved_by: str


# @app.post("/approve-command")
# def approve_command(req: ApproveCommandRequest, db: Session = Depends(get_db)):
#     approved = CommandList(
#         id=uuid.uuid4(),
#         task_description=req.task_description,
#         os_type=req.os_type,
#         final_command=req.final_command,
#         approved_by=req.approved_by,
#         approved_at=datetime.utcnow()
#     )
#     db.add(approved)
#     db.commit()
#     return {"status": "approved", "id": str(approved.id)}


# class AssignCommandRequest(BaseModel):
#     task_description: str
#     os_type: str
#     agent_id: str


# @app.post("/assign-command")
# def assign_command(req: AssignCommandRequest, db: Session = Depends(get_db)):
#     cmd = db.query(CommandList).filter(
#         CommandList.task_description == req.task_description,
#         CommandList.os_type == req.os_type
#     ).first()

#     if not cmd:
#         raise HTTPException(status_code=404, detail="Approved command not found")

#     new_task = Task(
#         task_id=str(uuid.uuid4()),
#         agent_id=req.agent_id,
#         os_type=req.os_type,
#         command=cmd.final_command,
#         status="queued"
#     )
#     db.add(new_task)
#     db.commit()
#     return {"status": "assigned", "task_id": new_task.task_id}

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# def fake_decode_token(token):
#     return {"username": token}

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#     return user

# # Logger setup
# logger = logging.getLogger("agentops")
# logging.basicConfig(level=logging.INFO)

# # ========= Utility Functions =========

# def get_mac_vendor(mac: str) -> str:
#     try:
#         response = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
#         if response.status_code == 200:
#             return response.text
#     except Exception as e:
#         logger.warning(f"MAC vendor lookup failed for {mac}: {e}")
#     return "unknown"

# def convert_objectid_to_str(doc):
#     if isinstance(doc, list):
#         return [convert_objectid_to_str(item) for item in doc]
#     if isinstance(doc, dict):
#         return {
#             key: str(value) if isinstance(value, ObjectId) else convert_objectid_to_str(value)
#             for key, value in doc.items()
#         }
#     return doc

# # ========= API Routes =========

# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     return {"access_token": form_data.username, "token_type": "bearer"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.get("/version")
# def version():
#     return {"version": "v1.0.0", "build": "stable"}

# @app.get("/api-list")
# def api_list():
#     return {"endpoints": [
#         "/register-agent", "/agent/{agent_id}", "/agents", "/generate-task",
#         "/approve-command", "/assign-command", "/get-task/{agent_id}", "/return-task",
#         "/task-result/{task_id}", "/commands", "/tasks", "/logs", "/logs/{task_id}",
#         "/log-summary/{agent_id}", "/vulnerabilities/{agent_id}", "/malware-report/{agent_id}",
#         "/software/{agent_id}", "/task-metrics", "/agent-status", "/auto-discover", "/audit-logs",
#         "/reassign-task", "/feedback", "/retrain-model", "/genai-suggest-command", "/genai-summarize/{task_id}",
#         "/agent-heartbeat", "/version", "/delete-agent/{agent_id}"
#     ]}

# @app.post("/agent-heartbeat")
# def heartbeat(agent_id: str, db: Session = Depends(get_db)):
#     agent = db.query(Agent).filter_by(agent_id=agent_id).first()
#     if agent:
#         agent.last_seen = datetime.utcnow()
#         db.commit()
#         return {"status": "alive"}
#     raise HTTPException(status_code=404, detail="Agent not found")

# @app.delete("/delete-agent/{agent_id}")
# def delete_agent(agent_id: str, db: Session = Depends(get_db)):
#     agent = db.query(Agent).filter_by(agent_id=agent_id).first()
#     if not agent:
#         raise HTTPException(status_code=404, detail="Agent not found")
#     db.delete(agent)
#     db.commit()
#     return {"status": "deleted", "agent_id": agent_id}

# @app.get("/vulnerabilities/{agent_id}")
# def get_vulnerabilities(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "vulnerabilities": [
#             {"id": "CVE-2023-1111", "severity": "high", "description": "OpenSSH buffer overflow"},
#             {"id": "CVE-2024-2222", "severity": "medium", "description": "Outdated NGINX version"}
#         ]
#     }

# @app.get("/malware-report/{agent_id}")
# def malware_report(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "status": "clean",
#         "last_scan": str(datetime.utcnow()),
#         "details": []
#     }

# @app.get("/software/{agent_id}")
# def list_software(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "installed_software": [
#             {"name": "nginx", "version": "1.18.0"},
#             {"name": "python3", "version": "3.12.0"},
#             {"name": "docker", "version": "24.0.5"}
#         ]
#     }

# @app.get("/audit-logs")
# def get_audit_logs():
#     return {
#         "logs": [
#             {"event": "task_assigned", "user": "admin", "timestamp": str(datetime.utcnow())},
#             {"event": "agent_registered", "agent": "agent-1", "timestamp": str(datetime.utcnow())}
#         ]
#     }



# # OAuth2 setup (simple JWT simulation for now)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# def fake_decode_token(token):
#     return {"username": token}

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#     return user

# # Logger setup
# logger = logging.getLogger("agentops")
# logging.basicConfig(level=logging.INFO)

# # ========= Utility Functions =========

# def get_mac_vendor(mac: str) -> str:
#     try:
#         response = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
#         if response.status_code == 200:
#             return response.text
#     except Exception as e:
#         logger.warning(f"MAC vendor lookup failed for {mac}: {e}")
#     return "unknown"

# def convert_objectid_to_str(doc):
#     if isinstance(doc, list):
#         return [convert_objectid_to_str(item) for item in doc]
#     if isinstance(doc, dict):
#         return {
#             key: str(value) if isinstance(value, ObjectId) else convert_objectid_to_str(value)
#             for key, value in doc.items()
#         }
#     return doc

# # ========= API Routes =========

# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     return {"access_token": form_data.username, "token_type": "bearer"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.get("/version")
# def version():
#     return {"version": "v1.0.0", "build": "stable"}

# @app.get("/api-list")
# def api_list():
#     return {"endpoints": [
#         "/register-agent", "/agent/{agent_id}", "/agents", "/generate-task",
#         "/approve-command", "/assign-command", "/get-task/{agent_id}", "/return-task",
#         "/task-result/{task_id}", "/commands", "/tasks", "/logs", "/logs/{task_id}",
#         "/log-summary/{agent_id}", "/vulnerabilities/{agent_id}", "/malware-report/{agent_id}",
#         "/software/{agent_id}", "/task-metrics", "/agent-status", "/auto-discover", "/audit-logs",
#         "/reassign-task", "/feedback", "/retrain-model", "/genai-suggest-command", "/genai-summarize/{task_id}",
#         "/agent-heartbeat", "/version", "/delete-agent/{agent_id}"
#     ]}

# @app.post("/agent-heartbeat")
# def heartbeat(agent_id: str, db: Session = Depends(get_db)):
#     agent = db.query(Agent).filter_by(agent_id=agent_id).first()
#     if agent:
#         agent.last_seen = datetime.utcnow()
#         db.commit()
#         return {"status": "alive"}
#     raise HTTPException(status_code=404, detail="Agent not found")

# @app.delete("/delete-agent/{agent_id}")
# def delete_agent(agent_id: str, db: Session = Depends(get_db)):
#     agent = db.query(Agent).filter_by(agent_id=agent_id).first()
#     if not agent:
#         raise HTTPException(status_code=404, detail="Agent not found")
#     db.delete(agent)
#     db.commit()
#     return {"status": "deleted", "agent_id": agent_id}

# @app.get("/vulnerabilities/{agent_id}")
# def get_vulnerabilities(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "vulnerabilities": [
#             {"id": "CVE-2023-1111", "severity": "high", "description": "OpenSSH buffer overflow"},
#             {"id": "CVE-2024-2222", "severity": "medium", "description": "Outdated NGINX version"}
#         ]
#     }

# @app.get("/malware-report/{agent_id}")
# def malware_report(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "status": "clean",
#         "last_scan": str(datetime.utcnow()),
#         "details": []
#     }

# @app.get("/software/{agent_id}")
# def list_software(agent_id: str):
#     return {
#         "agent_id": agent_id,
#         "installed_software": [
#             {"name": "nginx", "version": "1.18.0"},
#             {"name": "python3", "version": "3.12.0"},
#             {"name": "docker", "version": "24.0.5"}
#         ]
#     }

# @app.get("/audit-logs")
# def get_audit_logs():
#     return {
#         "logs": [
#             {"event": "task_assigned", "user": "admin", "timestamp": str(datetime.utcnow())},
#             {"event": "agent_registered", "agent": "agent-1", "timestamp": str(datetime.utcnow())}
#         ]
#     }

# # Additional endpoints will be continued below.

# @app.get("/agent-status")
# def agent_status():
#     return {"agents": [
#         {"agent_id": "agent-1", "uptime": "24h", "last_seen": str(datetime.utcnow())},
#         {"agent_id": "agent-2", "uptime": "6h", "last_seen": str(datetime.utcnow())}
#     ]}

# @app.get("/auto-discover")
# def auto_discover():
#     return {"message": "Auto-discovery not yet implemented"}

# @app.get("/task-metrics")
# def task_metrics():
#     return {
#         "total_tasks": 20,
#         "success": 18,
#         "failures": 2,
#         "average_execution_time": "5s"
#     }

# @app.get("/logs")
# def get_all_logs():
#     return {"logs": [
#         {"task_id": "1", "message": "Task completed", "timestamp": str(datetime.utcnow())}
#     ]}

# @app.get("/logs/{task_id}")
# def get_logs_for_task(task_id: str):
#     logs = get_logs_by_task(task_id)
#     return convert_objectid_to_str(logs)

# @app.get("/log-summary/{agent_id}")
# def summarize_agent_logs(agent_id: str):
#     return {"summary": summarize_logs(agent_id)}

# @app.post("/feedback")
# def feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
#     fb = Feedback(
#         id=uuid.uuid4(),
#         task_id=req.task_id,
#         feedback=req.feedback,
#         created_at=datetime.utcnow()
#     )
#     db.add(fb)
#     db.commit()
#     return {"status": "feedback recorded"}

# @app.post("/retrain-model")
# def retrain():
#     return {"status": "Retraining started (simulated)"}

# @app.post("/genai-suggest-command")
# def suggest(req: TaskRequest):
#     command = suggest_command(req.command, req.os_type)
#     return {"suggested_command": command}

# @app.get("/genai-summarize/{task_id}")
# def genai_summarize(task_id: str):
#     return {"summary": f"This is a simulated summary for task {task_id}"}

# @app.post("/reassign-task")
# def reassign_task(task_id: str, new_agent_id: str, db: Session = Depends(get_db)):
#     task = db.query(Task).filter(Task.task_id == task_id).first()
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     task.agent_id = new_agent_id
#     db.commit()
#     return {"status": "reassigned", "task_id": task_id, "new_agent_id": new_agent_id}

# @app.get("/commands")
# def list_commands(db: Session = Depends(get_db)):
#     commands = db.query(CommandList).all()
#     return jsonable_encoder(commands)

# @app.get("/tasks")
# def list_tasks(db: Session = Depends(get_db)):
#     tasks = db.query(Task).all()
#     return jsonable_encoder(tasks)
# main.py - FastAPI Backend with PostgreSQL and MongoDB (Enhanced and Optimized)

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId
import logging
import uuid
import platform
import socket
import requests
import jwt
import hashlib
from app.models import TaskRequest, TaskResult, AgentInfo, FeedbackRequest, TaskGenRequestMulti, ApproveCommandRequest, AssignCommandRequest
from app.db_pg import get_db, init_pg_db
from app.db_mongo import insert_log, get_logs_by_task
from app.models_pg import Agent, Task, GeneratedTask, CommandList, Feedback, User
from app.network_scanner import scan_network
from app.genai_utils import generate_command, summarize_logs, suggest_command

# Configuration
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 1440
# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger setup
logger = logging.getLogger("agentops")
logging.basicConfig(level=logging.INFO)

# Initialize PostgreSQL
init_pg_db()

# OAuth2 Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
# JWT Token Management
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def create_refresh_token(username: str):
    return jwt.encode({"sub": username, "type": "refresh", "exp": datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
def fake_decode_token(token):
    return {"username": token}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    username = payload.get("sub")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

def require_role(roles: List[str]):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

# Utility Functions

def get_mac_vendor(mac: str) -> str:
    try:
        response = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.warning(f"MAC vendor lookup failed for {mac}: {e}")
    return "unknown"

def convert_objectid_to_str(doc):
    if isinstance(doc, list):
        return [convert_objectid_to_str(item) for item in doc]
    if isinstance(doc, dict):
        return {
            key: str(value) if isinstance(value, ObjectId) else convert_objectid_to_str(value)
            for key, value in doc.items()
        }
    return doc

# Auth
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.password_hash != hashlib.sha256(form_data.password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user.username)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    username = payload.get("sub")
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}
# Health
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "v1.0.0", "build": "stable"}

@app.get("/api-list")
def api_list():
    return {"endpoints": [route.path for route in app.routes if hasattr(route, 'path')]}

# Agent Registration
@app.post("/register-agent")
def register_agent(agent: AgentInfo, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.agent_id == agent.agent_id).first()
    if not db_agent:
        new_agent = Agent(
            agent_id=agent.agent_id or str(uuid.uuid4()),
            os=agent.os or platform.system(),
            status=agent.status
        )
        db.add(new_agent)
        db.commit()
        return {"agent_id": new_agent.agent_id, "status": "registered"}
    return {"agent_id": db_agent.agent_id, "status": "already-registered"}

@app.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()

@app.get("/agent/{agent_id}")
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return jsonable_encoder(agent)

@app.get("/agent-status")
def agent_status():
    return {"agents": [
        {"agent_id": "agent-1", "uptime": "24h", "last_seen": str(datetime.utcnow())},
        {"agent_id": "agent-2", "uptime": "6h", "last_seen": str(datetime.utcnow())}
    ]}

@app.post("/agent-heartbeat")
def heartbeat(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter_by(agent_id=agent_id).first()
    if agent:
        agent.last_seen = datetime.utcnow()
        db.commit()
        return {"status": "alive"}
    raise HTTPException(status_code=404, detail="Agent not found")

@app.delete("/delete-agent/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"status": "deleted", "agent_id": agent_id}

@app.get("/agents/network-scan")
def agents_network_scan(db: Session = Depends(get_db)):
    registered_agents = db.query(Agent).all()
    registered_ips = {agent.ip: agent.agent_id for agent in registered_agents if agent.ip}
    scanned_devices = scan_network("192.168.1.0/24")
    response = []

    for device in scanned_devices:
        ip = device.get("ip")
        mac = device.get("mac")
        hostname = device.get("hostname", "unknown")
        vendor = device.get("vendor", get_mac_vendor(mac))
        os_type = device.get("os", "unknown")
        agent_id = registered_ips.get(ip)

        if agent_id:
            existing_agent = db.query(Agent).filter(Agent.ip == ip).first()
            existing_agent.mac = mac
            existing_agent.hostname = hostname
            existing_agent.vendor = vendor
            existing_agent.os = os_type
            db.commit()
            status = "updated"
        else:
            new_agent = Agent(
                agent_id=str(uuid.uuid4()),
                ip=ip,
                mac=mac,
                hostname=hostname,
                vendor=vendor,
                os=os_type,
                status="unregistered"
            )
            db.add(new_agent)
            db.commit()
            agent_id = new_agent.agent_id
            status = "registered"

        response.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "vendor": vendor,
            "os": os_type,
            "agent_id": agent_id,
            "status": status
        })

    return response

# Placeholders for missing endpoints
@app.post("/generate-task")
def generate_task():
    return {"message": "generate-task endpoint not implemented"}

@app.post("/approve-command")
def approve_command():
    return {"message": "approve-command endpoint not implemented"}

@app.post("/assign-command")
def assign_command():
    return {"message": "assign-command endpoint not implemented"}

@app.get("/commands")
def list_commands():
    return {"message": "commands listing not implemented"}

@app.get("/tasks")
def list_tasks():
    return {"message": "tasks listing not implemented"}

@app.get("/log-summary/{agent_id}")
def log_summary(agent_id: str):
    return {"summary": summarize_logs(agent_id)}

@app.get("/vulnerabilities/{agent_id}")
def get_vulnerabilities(agent_id: str):
    return {
        "agent_id": agent_id,
        "vulnerabilities": [
            {"id": "CVE-2023-1111", "severity": "high", "description": "OpenSSH buffer overflow"},
            {"id": "CVE-2024-2222", "severity": "medium", "description": "Outdated NGINX version"}
        ]
    }

@app.get("/malware-report/{agent_id}")
def malware_report(agent_id: str):
    return {
        "agent_id": agent_id,
        "status": "clean",
        "last_scan": str(datetime.utcnow()),
        "details": []
    }

@app.get("/software/{agent_id}")
def list_software(agent_id: str):
    return {
        "agent_id": agent_id,
        "installed_software": [
            {"name": "nginx", "version": "1.18.0"},
            {"name": "python3", "version": "3.12.0"},
            {"name": "docker", "version": "24.0.5"}
        ]
    }

@app.get("/auto-discover")
def auto_discover():
    return {"message": "Auto-discovery not yet implemented"}

@app.get("/audit-logs")
def get_audit_logs():
    return {
        "logs": [
            {"event": "task_assigned", "user": "admin", "timestamp": str(datetime.utcnow())},
            {"event": "agent_registered", "agent": "agent-1", "timestamp": str(datetime.utcnow())}
        ]
    }

@app.post("/reassign-task")
def reassign_task(task_id: str, new_agent_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.agent_id = new_agent_id
    db.commit()
    return {"status": "reassigned", "task_id": task_id, "new_agent_id": new_agent_id}

@app.post("/retrain-model")
def retrain_model():
    return {"status": "Retraining initiated (mock)"}

@app.post("/genai-suggest-command")
def genai_suggest_command(req: TaskRequest):
    command = suggest_command(req.command, req.os_type)
    return {"suggested_command": command}

@app.get("/genai-summarize/{task_id}")
def genai_summarize(task_id: str):
    return {"summary": f"This is a simulated summary for task {task_id}"}

# Existing Endpoints Continue...
@app.post("/submit-task")
def submit_task(task: TaskRequest, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    new_task = Task(
        task_id=task_id,
        command=task.command,
        os_type=task.os_type,
        agent_id=task.agent_id
    )
    db.add(new_task)
    db.commit()
    return {"status": "queued", "task_id": task_id}

@app.get("/get-task/{agent_id}")
def get_task(agent_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.agent_id == agent_id, Task.status == "queued").first()
    if task:
        task.status = "in_progress"
        db.commit()
        return {
            "task_id": task.task_id,
            "command": task.command,
            "os_type": task.os_type
        }
    return {"message": "no-task"}

@app.post("/return-task")
def return_task(result: TaskResult, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == result.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = result.status
    task.stdout = result.stdout
    task.stderr = result.stderr
    task.returncode = result.returncode
    db.commit()
    insert_log(result.task_id, result.dict())
    return {"status": "result-stored"}

@app.get("/task-result/{task_id}")
def get_result(task_id: str, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        logs = get_logs_by_task(task_id)
        logs = convert_objectid_to_str(logs) if logs else []
        return {"task": jsonable_encoder(task), "logs": logs}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@app.get("/logs")
def get_all_logs():
    return {"logs": [
        {"task_id": "1", "message": "Task completed", "timestamp": str(datetime.utcnow())}
    ]}

@app.get("/logs/{task_id}")
def get_logs_for_task(task_id: str):
    logs = get_logs_by_task(task_id)
    return convert_objectid_to_str(logs)

@app.post("/feedback")
def feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    fb = Feedback(
        id=uuid.uuid4(),
        task_id=req.task_id,
        feedback=req.feedback,
        created_at=datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    return {"status": "feedback recorded"}

@app.get("/metrics")
def task_metrics():
    return {
        "total_tasks": 20,
        "success": 18,
        "failures": 2,
        "average_execution_time": "5s"
    }

# End of main.py
# End of main.py