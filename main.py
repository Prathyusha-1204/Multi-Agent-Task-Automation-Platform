from fastapi import FastAPI
from api.routes import router
from database.db import engine
from database.models import Base

# Create all tables in Neon DB on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Agent Task Automation Platform",
    description="AI agents that break down goals and execute them automatically.",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Multi-Agent Task Platform is Running ✅"}