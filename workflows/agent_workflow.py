from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.planner_agent  import planner_agent
from agents.executor_agent import executor_agent
from agents.summary_agent  import summary_agent


# ── State Schema ──────────────────────────────────────────────
class AgentState(TypedDict):
    goal          : str
    subtasks      : list
    current_index : int
    results       : list
    status        : str
    final_summary : str


# ── Router — decides next node ────────────────────────────────
def should_continue(state: AgentState) -> str:
    """
    If there are still subtasks left → go back to executor.
    If all subtasks done → go to summarizer.
    """
    if state["current_index"] < len(state["subtasks"]):
        return "execute"
    return "summarize"


# ── Build the Graph ───────────────────────────────────────────
def build_workflow():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner",  planner_agent)
    graph.add_node("executor", executor_agent)
    graph.add_node("summary",  summary_agent)

    # Entry point
    graph.set_entry_point("planner")

    # Planner → executor always
    graph.add_edge("planner", "executor")

    # Executor → conditional (loop or summarize)
    graph.add_conditional_edges(
        "executor",
        should_continue,
        {
            "execute":   "executor",   # loop back
            "summarize": "summary"     # move forward
        }
    )

    # Summary → END
    graph.add_edge("summary", END)

    return graph.compile()


# ── Main entry point called by API ───────────────────────────
def run_workflow(goal: str) -> str:
    workflow = build_workflow()

    initial_state = AgentState(
        goal          = goal,
        subtasks      = [],
        current_index = 0,
        results       = [],
        status        = "starting",
        final_summary = ""
    )

    print(f"[Workflow] Starting for goal: {goal}")
    final_state = workflow.invoke(initial_state)
    print(f"[Workflow] Completed. Status: {final_state['status']}")

    return final_state["final_summary"]