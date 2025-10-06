from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    error_status: str = "success"