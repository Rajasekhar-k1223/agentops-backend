# main.py - FastAPI Backend with PostgreSQL and MongoDB

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models import TaskRequest, TaskResult, AgentInfo
from app.db_pg import get_db, init_pg_db
from app.db_mongo import insert_log, get_logs_by_task
from app.models_pg import Agent, Task
from app.network_scanner import scan_network
import uuid
import platform
import socket
import requests

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PostgreSQL
init_pg_db()


# ========= Utility Functions =========

def get_mac_vendor(mac: str) -> str:
    try:
        response = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"MAC vendor lookup failed for {mac}: {e}")
    return "unknown"


# ========= API Routes =========

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
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if task:
        logs = get_logs_by_task(task_id)
        return {"task": task, "logs": logs}
    return {"status": "not-found"}


@app.get("/agents/network-scan")
def agents_network_scan(db: Session = Depends(get_db)):
    registered_agents = db.query(Agent).all()
    registered_ips = {agent.ip: agent.agent_id for agent in registered_agents if agent.ip}

    scanned_devices = scan_network("192.168.1.0/24")  # Adjust subnet as needed
    response = []

    for device in scanned_devices:
        ip = device.get("ip")
        mac = device.get("mac")
        hostname = device.get("hostname", "unknown")
        vendor = device.get("vendor", "unknown")
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
