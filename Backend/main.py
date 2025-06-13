# ================================
#  DB Table Creation (One-Time)
# ================================
from app.models import models
from app.core.database import Base, engine

# Create tables if not already created
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

# ================================
#  FastAPI App Setup + Routers
# ================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from app.routes.ws import ws_router  # ✅ WebSocket router

# ✅ Create FastAPI instance
app = FastAPI()

# ✅ Include Routers
app.include_router(chat.router)
app.include_router(ws_router)

# ✅ Enable CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Batch Control AI Assistant is running!"}



