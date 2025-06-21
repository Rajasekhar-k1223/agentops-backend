# agent_executor.py - Execute Shell or PowerShell Commands Safely

import subprocess
import platform

def execute_command(command: str, os_type: str = None) -> dict:
    """
    Executes a command based on OS. Returns logs and status.
    """
    os_type = os_type or platform.system().lower()

    if "windows" in os_type:
        command = f"powershell -Command \"{command}\""

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "status": "success" if result.returncode == 0 else "error"
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "status": "exception"
        }

# ========== Test ==========
if __name__ == "__main__":
    output = execute_command("echo Hello from Agent")
    print("\n=== Agent Output ===")
    print(output)