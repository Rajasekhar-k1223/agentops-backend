# # app/genai_utils.py

# import os
# import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")

# def generate_command(task_description: str, os_type: str) -> str:
#     prompt = f"""You are an expert DevOps engineer. Based on the OS: {os_type}, provide a single shell command to: {task_description}. 
# Do not include explanations or extra output, just the command."""

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You generate shell commands for DevOps tasks."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2,
#             max_tokens=100,
#         )

#         command = response["choices"][0]["message"]["content"].strip()
#         return command
#     except Exception as e:
#         return f"Error generating command: {str(e)}"

# app/genai_utils.py

# import subprocess

# def generate_command(task_description: str, os_type: str) -> str:
#     prompt = f"You are an expert DevOps engineer. Based on the OS: {os_type}, provide a single shell command to: {task_description}. Only return the command."

#     try:
#         # Use Ollama to run a local LLM like llama3:8b or mistral
#         result = subprocess.run(
#             ["ollama", "run", "llama3:8b"],
#             input=prompt.encode("utf-8"),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             timeout=60
#         )

#         if result.returncode != 0:
#             return f"Error generating command: {result.stderr.decode('utf-8')}"

#         return result.stdout.decode("utf-8").strip()
    
#     except subprocess.TimeoutExpired:
#         return "Error generating command: Request timed out"
#     except Exception as e:
#         return f"Error generating command: {str(e)}"

# import subprocess
# import uuid
# from sqlalchemy.orm import Session
# from datetime import datetime
# from app.models_pg import GeneratedTask

# def generate_command(task_description: str, os_type: str, db: Session, created_by: str = "system", model_used: str = "llama3:8b") -> dict:
#     """
#     Generate a shell command using Ollama's LLM and store it in the GeneratedTask table.
#     """
#     prompt = f"You are an expert DevOps engineer. Based on the OS: {os_type}, provide a single shell command to: {task_description}. Only return the command."

#     try:
#         result = subprocess.run(
#             ["ollama", "run", model_used],
#             input=prompt.encode("utf-8"),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             timeout=60
#         )

#         if result.returncode != 0:
#             return {"status": "error", "message": result.stderr.decode("utf-8")}

#         generated_command = result.stdout.decode("utf-8").strip()

#         # Save in DB
#         generated_task = GeneratedTask(
#             id=uuid.uuid4(),
#             task_description=task_description,
#             os_type=os_type,
#             generated_command=generated_command,
#             model_used=model_used,
#             created_by=created_by,
#             created_at=datetime.utcnow()
#         )

#         db.add(generated_task)
#         db.commit()

#         return {
#             "status": "success",
#             "command": generated_command,
#             "task_id": str(generated_task.id),
#             "model_used": model_used
#         }

#     except subprocess.TimeoutExpired:
#         return {"status": "error", "message": "Command generation timed out"}

#     except Exception as e:
#         return {"status": "error", "message": str(e)}

import subprocess

def generate_command(task_description: str, os_type: str) -> str:
    prompt = f"You are an expert DevOps engineer. Based on the OS: {os_type}, provide a single shell command to: {task_description}. Only return the command."

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3:8b"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        if result.returncode != 0:
            return f"Error generating command: {result.stderr.decode('utf-8')}"

        return result.stdout.decode("utf-8").strip()

    except subprocess.TimeoutExpired:
        return "Error generating command: Request timed out"
    except Exception as e:
        return f"Error generating command: {str(e)}"


def summarize_logs(agent_id: str) -> str:
    # Dummy example: Replace with real summarization logic or LLM call
    return f"Summary for logs of agent {agent_id}: All tasks executed with no major errors."


def suggest_command(input_text: str, os_type: str = "linux") -> str:
    # Dummy suggestion logic: Use real LLM or rule-based logic here
    return f"Suggested command for '{input_text}' on {os_type}: echo 'Hello World'"

