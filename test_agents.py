from agents.planner_agent import planner_agent
from agents.executor_agent import execute_task
from agents.summary_agent import summarize_results

# Test 1 - Planner
print("=" * 50)
print("Testing Planner Agent...")
goal = "Write a blog post about AI trends in 2025"
tasks = planner_agent(goal)
print(f"Subtasks generated: {len(tasks)}")
for i, t in enumerate(tasks):
    print(f"  {i+1}. {t}")

# Test 2 - Executor
print("\n" + "=" * 50)
print("Testing Executor Agent...")
result = execute_task(tasks[0])
print(f"Result preview: {result[:200]}...")

# Test 3 - Summary
print("\n" + "=" * 50)
print("Testing Summary Agent...")
fake_results = ["Research done on AI.", "Outline created.", "Draft written."]
summary = summarize_results(goal, fake_results)
print(f"Summary preview: {summary[:300]}...")

print("\n✅ All agents working!")