from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from fastapi.responses import JSONResponse

from assistant import app as personal_assistant_app

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

@app_fastapi.get("/")
def read_root():
    return {"status": "AI Personal Assistant API is running."}