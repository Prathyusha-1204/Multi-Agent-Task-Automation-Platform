# This file can hold reusable dashboard components if needed.
# Currently all UI logic is in app.py

def format_status(status: str) -> str:
    icons = {
        "pending":   "⏳ Pending",
        "running":   "🔄 Running",
        "completed": "✅ Completed",
        "failed":    "❌ Failed"
    }
    return icons.get(status, status)