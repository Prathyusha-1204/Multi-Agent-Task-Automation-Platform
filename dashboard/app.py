import streamlit as st
import requests
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Multi-Agent Task Platform",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Task Automation Platform")
st.caption("Powered by LangGraph + Groq LLM")

# ── Submit Goal ───────────────────────────────────────────────
st.subheader("🎯 Submit a Goal")

goal = st.text_area(
    "Enter your goal",
    height=80,
    placeholder="e.g. Explain Prompt Engineering"
)

if st.button("🚀 Run Agents", type="primary"):
    if not goal.strip():
        st.warning("Please enter a goal first.")
    else:
        st.markdown("---")
        st.markdown("### 🤖 Agent Activity")

        # Agent status cards
        col1, col2, col3 = st.columns(3)

        with col1:
            planner_card = st.empty()
            planner_card.info("🧠 **Planner Agent**\n\nWaiting...")

        with col2:
            executor_card = st.empty()
            executor_card.info("⚙️ **Executor Agent**\n\nWaiting...")

        with col3:
            summary_card = st.empty()
            summary_card.info("📝 **Summary Agent**\n\nWaiting...")

        st.markdown("")
        progress_bar = st.progress(0)
        status_text  = st.empty()

        # Live log
        st.markdown("#### 📜 Live Agent Log")
        log_box = st.empty()
        logs = []

        try:
            with requests.get(
                f"{API_URL}/run-task-stream",
                params={"goal": goal},
                stream=True,
                timeout=300
            ) as response:

                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            data     = json.loads(line[6:])
                            msg_type = data.get("type")
                            message  = data.get("message", "")

                            if msg_type == "status":
                                # Planner started
                                planner_card.warning("🧠 **Planner Agent**\n\n⏳ Breaking down goal...")
                                status_text.info(message)
                                logs.append(f"🧠 Planner Agent → {message}")

                            elif msg_type == "planned":
                                # Planner done
                                subtasks = data.get("subtasks", [])
                                planner_card.success(f"🧠 **Planner Agent**\n\n✅ Created {len(subtasks)} subtasks!")
                                executor_card.warning("⚙️ **Executor Agent**\n\n⏳ Starting execution...")
                                logs.append(f"🧠 Planner Agent → ✅ Done! Created {len(subtasks)} subtasks")

                                # Show subtask list
                                with st.expander("📋 View Planned Subtasks", expanded=True):
                                    for i, t in enumerate(subtasks):
                                        st.markdown(f"`{i+1}.` {t}")

                            elif msg_type == "executing":
                                index   = data.get("index", 0)
                                total   = data.get("total", 1)
                                subtask = message.replace(f"⚙️ Running subtask {index}/{total}: ", "")
                                progress_bar.progress(int((index - 1) / total * 100))
                                executor_card.warning(f"⚙️ **Executor Agent**\n\n⏳ Running {index}/{total}:\n_{subtask}_")
                                status_text.warning(message)
                                logs.append(f"⚙️ Executor Agent → Running subtask {index}/{total}: {subtask}")

                            elif msg_type == "completed":
                                index = data.get("index", 0)
                                total = data.get("total", 1)
                                progress_bar.progress(int(index / total * 100))
                                executor_card.success(f"⚙️ **Executor Agent**\n\n✅ Subtask {index}/{total} done!")
                                logs.append(f"⚙️ Executor Agent → ✅ Subtask {index}/{total} completed")

                            elif msg_type == "done":
                                # All done
                                progress_bar.progress(100)
                                executor_card.success("⚙️ **Executor Agent**\n\n✅ All subtasks done!")
                                summary_card.success("📝 **Summary Agent**\n\n✅ Report ready!")
                                status_text.success("✅ All agents completed successfully!")
                                logs.append("📝 Summary Agent → ✅ Final report generated!")

                                st.markdown("---")
                                st.subheader("📋 Final Summary Report")
                                st.markdown(data.get("summary", ""))

                            elif msg_type == "error":
                                status_text.error(message)
                                planner_card.error("🧠 **Planner Agent**\n\n❌ Error")
                                executor_card.error("⚙️ **Executor Agent**\n\n❌ Error")
                                summary_card.error("📝 **Summary Agent**\n\n❌ Error")
                                logs.append(f"❌ Error → {message}")

                            # Update live log
                            log_box.markdown(
                                "\n".join([f"- {l}" for l in logs])
                            )

        except Exception as e:
            st.error(f"Connection error: {e}")

st.divider()

# ── Dashboard ─────────────────────────────────────────────────
st.subheader("📊 Task Execution Dashboard")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()

try:
    resp = requests.get(f"{API_URL}/tasks", timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()
        if tasks:
            df = pd.DataFrame(tasks)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Tasks",   len(df))
            col2.metric("✅ Completed",  len(df[df["status"] == "completed"]))
            col3.metric("⏳ Running",    len(df[df["status"] == "running"]))
            col4.metric("❌ Failed",     len(df[df["status"] == "failed"]))

            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "completed", "running", "pending", "failed"]
            )
            if status_filter != "All":
                df = df[df["status"] == status_filter]

            st.dataframe(
                df[["id", "goal", "subtask", "status", "result", "created_at"]],
                use_container_width=True
            )
        else:
            st.info("No tasks yet. Submit a goal above to get started!")
    else:
        st.error("Could not fetch tasks from API.")
except Exception as e:
    st.error(f"Dashboard error: {e}")


