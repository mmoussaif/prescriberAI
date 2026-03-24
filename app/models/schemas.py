from pydantic import BaseModel


class Provider(BaseModel):
    name: str
    role: str
    npi: str


class PracticeInfo(BaseModel):
    npi: str
    practice_name: str
    address: str
    specialty: str
    providers: list[Provider]


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    practice_context: PracticeInfo
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    current_phase: str
    needs_escalation: bool = False
    sidebar_caption: str | None = None
    validation_quality: str = "ok"


class ErrorResponse(BaseModel):
    error: str
