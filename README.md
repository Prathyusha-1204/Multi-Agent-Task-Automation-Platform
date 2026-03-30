# Multi-Agent Task Automation Platform

An AI-driven platform that automates complex tasks using multiple specialized AI agents.

## Features
- 🧠 Planner Agent — breaks goals into subtasks
- ⚙️ Executor Agent — executes each subtask via Groq LLM
- 📝 Summary Agent — generates final report
- 🔄 LangGraph orchestration
- ⚡ Real-time streaming updates
- 🗄️ Neon PostgreSQL storage

## Tech Stack
- Python, FastAPI, Streamlit
- LangGraph, Groq LLM
- Neon PostgreSQL, SQLAlchemy

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add `.env` file with your credentials
4. Run FastAPI: `uvicorn main:app --reload`
5. Run Streamlit: `streamlit run dashboard/app.py`
