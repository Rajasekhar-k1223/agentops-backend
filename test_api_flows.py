# test_api_flows.py

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def get_agents():
    response = requests.get(f"{BASE_URL}/agents")
    print("[get-agents]", response.status_code, response.json())
    assert response.status_code == 200
    return response.json()

def test_generate_task():
    payload = {
        "task_description": "check if nginx is installed",
        "os_list": ["linux", "windows", "mac"],
        "created_by": "admin",
        "model_used": "ollama"
    }
    response = requests.post(f"{BASE_URL}/generate-task", json=payload)
    print("[generate-task]", response.status_code, response.json())
    assert response.status_code == 200
    return response.json()

def test_approve_command(generated_task_id, task_description, os_type, final_command):
    payload = {
        "generated_task_id": generated_task_id,
        "task_description": task_description,
        "os_type": os_type,
        "final_command": final_command,
        "approved_by": "admin"
    }
    response = requests.post(f"{BASE_URL}/approve-command", json=payload)
    print("[approve-command]", response.status_code, response.json())
    assert response.status_code == 200

def test_assign_command(task_description, os_type, agent_id):
    payload = {
        "task_description": task_description,
        "os_type": os_type,
        "agent_id": agent_id
    }
    response = requests.post(f"{BASE_URL}/assign-command", json=payload)
    print("[assign-command]", response.status_code, response.json())
    assert response.status_code == 200
    return response.json()["task_id"]

def test_get_task(agent_id, retries=3, delay=1):
    for attempt in range(retries):
        response = requests.get(f"{BASE_URL}/get-task/{agent_id}")
        print(f"[get-task] Attempt {attempt + 1}: {response.status_code}")
        data = response.json()
        if response.status_code == 200 and "command" in data:
            print(data)
            return data
        time.sleep(delay)
    raise AssertionError(f"❌ No task retrieved for agent {agent_id} after {retries} attempts")

def test_return_task(task_id, agent_id):
    payload = {
        "task_id": task_id,
        "agent_id": agent_id,
        "status": "completed",
        "stdout": "nginx-core 1.18.0-6ubuntu14",
        "stderr": "",
        "returncode": 0
    }
    response = requests.post(f"{BASE_URL}/return-task", json=payload)
    print("[return-task]", response.status_code)
    try:
        print(response.json())
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        print("Raw response:", response.text)
    if response.status_code != 200:
        raise AssertionError(f"❌ Failed to return task result: {response.status_code}")

def test_get_task_result(task_id):
    print(task_id)
    response = requests.get(f"{BASE_URL}/task-result/{task_id}")
    print(response)
    print("[task-result]", response.status_code)
    try:
        data = response.json()
        print(data)
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        print("Raw response:", response.text)
        raise AssertionError("❌ Failed to get task result - Invalid JSON response")
    assert response.status_code == 200

if __name__ == "__main__":
    agents = get_agents()
    if not agents:
        print("❌ No agents registered. Please register agents first.")
        exit(1)

    task_data = test_generate_task()
    task_description = task_data["description"]
    generated_tasks = task_data["generated_tasks"]

    for agent in agents:
        agent_id = agent["agent_id"]
        agent_os_raw = agent["os"] or "unknown"
        normalized_os = "linux" if "linux" in agent_os_raw.lower() else (
            "windows" if "windows" in agent_os_raw.lower() else (
                "mac" if "mac" in agent_os_raw.lower() or "darwin" in agent_os_raw.lower() else "unknown"
            )
        )

        matched_task = next(
            (item for item in generated_tasks if item["os"].lower() == normalized_os),
            None
        )

        if matched_task:
            print(f"\n✅ Testing agent `{agent_id}` with normalized OS `{normalized_os}`")
            generated_task_id = matched_task.get("generated_task_id")
            final_command = matched_task["generated_command"]

            if not generated_task_id:
                print(f"⚠️ Missing generated_task_id for OS `{normalized_os}`, skipping.")
                continue

            test_approve_command(generated_task_id, task_description, normalized_os, final_command)
            task_id = test_assign_command(task_description, normalized_os, agent_id)
            test_get_task(agent_id)
            test_return_task(task_id, agent_id)
            test_get_task_result(task_id)
        else:
            print(f"⚠️ No command found for OS: {normalized_os}, skipping agent {agent_id}")
