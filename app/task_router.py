# task_router.py - OS Detection and Command Routing for AgentOps

import platform

def detect_os_type() -> str:
    os_name = platform.system().lower()
    if "windows" in os_name:
        return "windows"
    elif "linux" in os_name:
        return "linux"
    elif "darwin" in os_name or "mac" in os_name:
        return "macos"
    return "unknown"

def route_command(task: str, os_type: str = None) -> str:
    os_type = os_type or detect_os_type()

    # Basic template mapping (extendable)
    templates = {
        "install nginx": {
            "linux": "sudo apt install nginx -y",
            "macos": "brew install nginx",
            "windows": "choco install nginx"
        },
        "start nginx": {
            "linux": "sudo systemctl start nginx",
            "macos": "brew services start nginx",
            "windows": "Start-Service nginx"
        }
    }

    task_key = task.lower().strip()
    return templates.get(task_key, {}).get(os_type, task)  # fallback: return original command
