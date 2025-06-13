from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.rag.rag_pipeline import get_sql_from_question
import traceback
import redis
import hashlib
import re

# ✅ Redis setup
cache = redis.Redis(host="localhost", port=6379, db=0)

# ✅ Simple in-memory session memory
chat_context = {
    "last_batch_code": None,
}

router = APIRouter()

class Message(BaseModel):
    message: str = Field(..., alias="query")
    class Config:
        validate_by_name = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=str)
async def chat_route(request: Message) -> Any:
    try:
        question = request.message.strip()

        # ✅ Greeting detection
        if question.lower() in ["hello", "hi", "hey", "how are you", "thank you"]:
            return "👋 Hi! I'm your Batch Control Assistant. How can I help you today?"

        # ✅ Track batch code context
        batch_match = re.search(r'\b([A-Z]{3}-\d{6}-[A-Z])\b', question)
        if batch_match:
            chat_context["last_batch_code"] = batch_match.group(1)
        elif re.search(r"\bit\b|\bthat batch\b", question.lower()) and chat_context.get("last_batch_code"):
            question += f" for batch {chat_context['last_batch_code']}"

        # ✅ Redis Caching
        question_hash = hashlib.sha256(question.encode()).hexdigest()
        cached_response = cache.get(question_hash)
        if cached_response:
            return cached_response.decode()

        # ✅ Get SQL from LLM
        sql_query = get_sql_from_question(question)

        if sql_query.startswith("-- ERROR") or sql_query.strip() == "-- No valid SQL found":
            return "🤖 Sorry, I couldn't understand your question. Try asking about batches, employees, or products."

        db: Session = next(get_db())
        try:
            result = db.execute(text(sql_query))
        except Exception as db_err:
            return f"❌ SQL execution failed:\n{sql_query}\n\nError: {str(db_err)}"

        rows = result.mappings().all()
        formatted = [row for row in rows]

        if not formatted:
            final_response = "📭 No results found for your query."
        elif len(formatted) == 1:
            final_response = ", ".join(f"{k}: {v}" for k, v in formatted[0].items())
        else:
            lines = ["• " + ", ".join(f"{k}: {v}" for k, v in row.items()) for row in formatted]
            final_response = "📦 Here are the results:\n" + "\n".join(lines)

        # ✅ Store in Redis
        cache.set(question_hash, final_response)

        return final_response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
