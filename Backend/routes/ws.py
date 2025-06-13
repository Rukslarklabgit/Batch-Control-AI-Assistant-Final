from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.rag.rag_pipeline import get_sql_from_question

ws_router = APIRouter()  # ✅ Use consistent router name

@ws_router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    db: Session = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text("typing...")

            sql_query = get_sql_from_question(data)
            if sql_query.startswith("-- ERROR") or sql_query.strip() == "-- No valid SQL found":
                await websocket.send_text("🤖 Sorry, I couldn't understand your question.")
                continue

            try:
                result = db.execute(text(sql_query))
                rows = result.mappings().all()
            except Exception as e:
                await websocket.send_text(f"❌ SQL execution failed:\n{str(e)}")
                continue

            if not rows:
                await websocket.send_text("📭 No results found for your query.")
            elif len(rows) == 1:
                message = ", ".join(f"{k}: {v}" for k, v in rows[0].items())
                await websocket.send_text(message)
            else:
                lines = ["• " + ", ".join(f"{k}: {v}" for k, v in row.items()) for row in rows]
                await websocket.send_text("📦 Here are the results:\n" + "\n".join(lines))

    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    finally:
        db.close()
