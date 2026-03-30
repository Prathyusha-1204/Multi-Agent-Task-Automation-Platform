import os
from groq import Groq
from dotenv import load_dotenv
from database.db import SessionLocal
from database.models import Task

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def executor_agent(state: dict) -> dict:
    """
    LangGraph node — executes current subtask, saves to DB.
    """
    db = SessionLocal()

    try:
        subtasks     = state["subtasks"]
        current_index = state["current_index"]
        goal         = state["goal"]
        subtask      = subtasks[current_index]

        print(f"[Executor] Running subtask {current_index + 1}: {subtask[:60]}...")

        # Save as pending
        db_task = Task(
            goal    = goal,
            subtask = subtask,
            status  = "pending",
            result  = ""
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        # Mark running
        db_task.status = "running"
        db.commit()

        prompt = f"""
You are an expert task executor.
Complete the following task thoroughly and concisely.

Task: {subtask}

Provide a clear, well-structured response.
"""

        chat = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        result = chat.choices[0].message.content

        # Save completed
        db_task.status = "completed"
        db_task.result = result
        db.commit()

        state["results"].append(result)
        state["current_index"] += 1
        state["status"] = "executing"

        return state

    except Exception as e:
        print(f"[Executor Error] {e}")
        state["results"].append(f"Error: {str(e)}")
        state["current_index"] += 1
        state["status"] = "executing"
        return state

    finally:
        db.close()