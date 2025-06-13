from app.models import models
from app.core.database import Base, engine

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All tables created successfully!")
