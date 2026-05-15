from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core.memory import Memory


router = APIRouter(prefix="/memory", tags=["memory"])
memory_store = Memory()


class SessionCreateRequest(BaseModel):
    session_id: str
    title: str = "محادثة جديدة"


class RenameSessionRequest(BaseModel):
    title: str


@router.get("")
def memory():
    memory_store._load_long_term()
    return {"memory": "active", "stats": memory_store.get_stats()}


@router.get("/sessions")
def sessions():
    memory_store._load_long_term()
    return {"sessions": memory_store.list_sessions()}


@router.post("/sessions")
def create_session(request: SessionCreateRequest):
    return {"session": memory_store.ensure_session(request.session_id, request.title)}


@router.get("/sessions/{session_id}")
def session_history(session_id: str, limit: Optional[int] = 200):
    memory_store._load_long_term()
    return {
        "session_id": session_id,
        "messages": memory_store.get_conversation_history(session_id, limit=limit or 200),
    }


@router.patch("/sessions/{session_id}")
def rename_session(session_id: str, request: RenameSessionRequest):
    return {"success": memory_store.rename_session(session_id, request.title)}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    return {"success": memory_store.delete_session(session_id)}
