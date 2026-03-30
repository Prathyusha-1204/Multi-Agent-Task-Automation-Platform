import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def summary_agent(state: dict) -> dict:
    """
    LangGraph node — summarizes all results into final report.
    """
    goal    = state["goal"]
    results = state["results"]

    combined = "\n\n".join(
        [f"Subtask {i+1} Result:\n{r}" for i, r in enumerate(results)]
    )

    prompt = f"""
You are an expert summarizer.
The user had this goal: "{goal}"

Here are the results from each subtask:

{combined}

Write a clear, professional final summary report that:
- Answers the user's original goal
- Highlights key findings from each subtask
- Is structured with short paragraphs
"""

    try:
        chat = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        state["final_summary"] = chat.choices[0].message.content
        state["status"] = "completed"
        print("[Summary] Final report generated.")
        return state

    except Exception as e:
        print(f"[Summary Error] {e}")
        state["final_summary"] = "\n\n".join(results)
        state["status"] = "completed"
        return state