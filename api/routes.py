from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from workflows.agent_workflow import run_workflow, build_workflow
from database.db import SessionLocal
from database.models import Task
from agents.planner_agent import planner_agent
from agents.executor_agent import executor_agent
from agents.summary_agent import summary_agent
from workflows.agent_workflow import AgentState
import json

router = APIRouter()


@router.post("/run-task")
def run_task(goal: str):
    """Standard non-streaming endpoint."""
    if not goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")
    try:
        result = run_workflow(goal)
        return {"status": "success", "goal": goal, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/run-task-stream")
def run_task_stream(goal: str):
    """
    Streaming endpoint — sends updates as each subtask completes.
    """
    if not goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    def event_generator():
        try:
            # Step 1 - Planning
            yield f"data: {json.dumps({'type': 'status', 'message': '🧠 Planner Agent is breaking down your goal...'})}\n\n"

            state = AgentState(
                goal          = goal,
                subtasks      = [],
                current_index = 0,
                results       = [],
                status        = "starting",
                final_summary = ""
            )

            # Run planner
            state = planner_agent(state)
            total = len(state["subtasks"])

            yield f"data: {json.dumps({'type': 'planned', 'message': f'📋 Created {total} subtasks', 'subtasks': state['subtasks']})}\n\n"

            # Step 2 - Execute each subtask
            for i in range(total):
                subtask = state["subtasks"][i]
                yield f"data: {json.dumps({'type': 'executing', 'message': f'⚙️ Running subtask {i+1}/{total}: {subtask}', 'index': i+1, 'total': total})}\n\n"

                state = executor_agent(state)

                yield f"data: {json.dumps({'type': 'completed', 'message': f'✅ Subtask {i+1}/{total} completed', 'index': i+1, 'total': total})}\n\n"

            # Step 3 - Summary
            yield f"data: {json.dumps({'type': 'status', 'message': '📝 Summary Agent is generating final report...'})}\n\n"

            state = summary_agent(state)

            yield f"data: {json.dumps({'type': 'done', 'message': '🎉 All done!', 'summary': state['final_summary']})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/tasks")
def get_tasks():
    """Fetch all tasks from the database."""
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.id.desc()).all()
        return [
            {
                "id":         t.id,
                "goal":       t.goal,
                "subtask":    t.subtask,
                "status":     t.status,
                "result":     t.result,
                "created_at": str(t.created_at)
            }
            for t in tasks
        ]
    finally:
        db.close()