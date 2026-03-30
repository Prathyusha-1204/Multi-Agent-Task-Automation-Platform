import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def planner_agent(state: dict) -> dict:
    """
    LangGraph node — receives state, adds subtasks to it.
    """
    goal = state["goal"]

    prompt = f"""
You are a smart task planner.
Break the following goal into clear, actionable subtasks.

Goal: {goal}

Rules:
- Return ONLY a numbered list, one task per line.
- No explanations, no headers, no extra text.
- Minimum 3 tasks, maximum 6 tasks.
- Example format:
  1. Research the topic
  2. Write an outline
  3. Draft the content

Now generate the task list:
"""

    try:
        chat = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        raw_text = chat.choices[0].message.content

        tasks = []
        for line in raw_text.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                parts = line.split(".", 1)
                if len(parts) == 2:
                    tasks.append(parts[1].strip())

        state["subtasks"] = tasks if tasks else ["Research the goal", "Execute the plan", "Summarize results"]
        state["current_index"] = 0
        state["results"] = []
        state["status"] = "planned"

        print(f"[Planner] Created {len(state['subtasks'])} subtasks")
        return state

    except Exception as e:
        print(f"[Planner Error] {e}")
        state["subtasks"] = ["Research the goal", "Execute the plan", "Summarize results"]
        state["current_index"] = 0
        state["results"] = []
        state["status"] = "planned"
        return state