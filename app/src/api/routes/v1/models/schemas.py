from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    model: str
    model_provider: str
    message: str

class ChatResponse(BaseModel):
    response: str 