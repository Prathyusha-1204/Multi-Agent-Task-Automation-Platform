from database.db import engine
from database.models import Base

print("Creating tables in Neon DB...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")