from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    employee_id: str
    message: str
    target_employee_id: str | None = None
    role: str = "employee"


class ChatResponse(BaseModel):
    intent: str | None = None
    result: dict | None = None
    policy: dict | None = None
    status: str | None = None
    rbac: dict | None = None
    error: str | None = None


orchestrator = Orchestrator()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = orchestrator.process(request.employee_id, request.message, request.target_employee_id, request.role)
        return ChatResponse(
            intent=response.get("intent"),
            result=response.get("result"),
            policy=response.get("policy"),
            status=response.get("status"),
            rbac=response.get("rbac"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
