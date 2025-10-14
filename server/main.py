from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from fastapi.responses import JSONResponse

from assistant import app as personal_assistant_app, memory, conn

app_fastapi = FastAPI(
    title="AI Personal Assistant API",
    description="An API to interact with the personal assistant."
)

app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app_fastapi.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message:
        return JSONResponse(content={"error": "Message not provided"}, status_code=400)

    config = {"configurable": {"thread_id": request.thread_id}}
    response = personal_assistant_app.invoke({"messages": [HumanMessage(content=request.message)]}, config)
    
    final_response_content = response["messages"][-1].content
    
    return {"reply": final_response_content}

@app_fastapi.get("/api/history/{thread_id}")
async def get_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    conversation = memory.get(config)
    
    messages = []
    if conversation and conversation["messages"]:
        for msg in conversation["messages"]:
            messages.append({"sender": "user" if isinstance(msg, HumanMessage) else "assistant", "text": msg.content})

    return {"messages": messages}



@app_fastapi.get("/api/threads")
async def get_threads():
    """Veritabanındaki tüm benzersiz thread_id'leri listeler."""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
    threads = cursor.fetchall()
    thread_ids = [thread[0] for thread in threads]
    return {"threads": thread_ids}

@app_fastapi.get("/")
def read_root():
    return {"status": "AI Personal Assistant API is running."}