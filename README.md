#  Batch Control AI Assistant

An intelligent chatbot system for managing batch tracking in pharmaceutical operations. Supports natural language queries, real-time interaction, SQL generation via Gemini, and hybrid chat UI with WebSocket & REST.

---

##  Features

- 🧠 Natural Language to SQL using Gemini
- 📦 Batch tracking (Packed, Inspected, Stored, Dispatched)
- 🔍 Query employees, departments, products, status
- 🧭 Context memory for follow-up questions
- ⚡ FastAPI backend + React frontend
- 🧠 FAISS vector store with schema metadata
- 🌐 Real-time WebSocket + REST fallback
- 🗃️ Redis caching
- 📊 Test cases and API demo-ready

---

##  Tech Stack

| Layer         | Technology                      |
|--------------|----------------------------------|
| Frontend      | React, TypeScript, Tailwind      |
| Backend       | FastAPI, LangChain, Gemini Pro   |
| Database      | PostgreSQL                       |
| Embeddings    | Google Generative AI Embeddings  |
| Vector Store  | FAISS                            |
| Cache         | Redis                            |
| Realtime      | WebSockets                       |

---

##  Folder Structure

📁 batch-control-backend
├── app
│ ├── core (DB setup)
│ ├── models (SQLAlchemy)
│ ├── routes (chat.py, ws.py)
│ ├── rag (rag_pipeline.py)
├── seed.py
├── main.py
├── requirements.txt

📁 batch-control-frontend
├── src
│ ├── App.tsx
│ ├── App.css

---

##  Installation

### 1.  Backend Setup

```bash
cd batch-control-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py  #  Seed DB with 10+ records
uvicorn main:app --reload

### 1.  Frontend Setup

cd batch-control-frontend
npm install
npm run dev

### Sample cURL Test

curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Who delivered CSY-052025-C?\"}"

## 📸 Screenshots

| Description                        | Screenshot |
|------------------------------------|------------|
|  Backend Connection              | ![Backend](Screenshot+Demo/Screenshot/Backend Connection.png) |
|  Frontend Connection             | ![Frontend](Screenshot+Demo/Screenshot/Frontend Connection.png) |
|  Chatbot Working View 1         | ![Chat 1](Screenshot+Demo/Screenshot/Chatbot Working 1.png) |
|  Chatbot Working View 2         | ![Chat 2](Screenshot+Demo/Screenshot/Chatbot Working 2.png) |
|  Chatbot Working View 3         | ![Chat 3](Screenshot+Demo/Screenshot/Chatbot Working 3.png) |
|  Chatbot Working View 4         | ![Chat 4](Screenshot+Demo/Screenshot/Chatbot Working 4.png) |
|  Redis Connection Status        | ![Redis](Screenshot+Demo/Screenshot/Redis Connection 1.png) |
|  WebSocket Activated            | ![WS](Screenshot+Demo/Screenshot/Web Socket Activation.png) |
|  Swagger SQL Test (Bonus)       | ![Swagger](Screenshot+Demo/Screenshot/Swagger UI-SQL Query Response.png) |
|  venv Activated (Python)        | ![Venv](Screenshot+Demo/Screenshot/venv activation.png) |

## 🎥 Demo Videos

| Topic                            | Watch |
|----------------------------------|--------|
|  Terminal Setup + DB Seeding   | ▶️ [Project Terminal](Screenshot+Demo/Demo/Project Terminal 1.mp4) |
|  RAG + Database Queries        | ▶️ [RAG + DB Demo](Screenshot+Demo/Demo/RAG+DB.mp4) |
|  Full Chatbot Interaction     | ▶️ [Chatbot in Action](Screenshot+Demo/Demo/Working of Chatbot.mp4) |

##  Author

Ruksaana – Batch Control Assistant – 2025
