from fastapi import APIRouter

from pydantic import BaseModel
from typing import Optional

from core.model_execution.execution_engine import ModelExecutionEngine

from core.model_execution.ollama_runtime import OllamaRuntime
from core.intent import IntentClassifier
from core.media import MediaGenerationService
from core.search import WebSearchService
from core.memory import Memory


router = APIRouter()


engine = ModelExecutionEngine()


engine.pool.register(

    "ollama",

    OllamaRuntime()
)
memory_store = Memory()


class ChatRequest(BaseModel):

    message: str
    session_id: Optional[str] = None


@router.post("/chat")
def chat(request: ChatRequest):

    try:
        session_id = request.session_id or "web-default"
        memory_store.save_message(session_id, "user", request.message)
        history = memory_store.get_conversation_history(session_id, limit=30)
        history_prompt = _with_history(request.message, history)
        intent = IntentClassifier.detect(request.message)

        if intent.action == "image":
            result = MediaGenerationService.generate_image(request.message)
            response = result.get("message") if result.get("success") else result.get("error")
            memory_store.save_message(session_id, "assistant", response or "")
            return {"response": response, "intent": intent.action, "result": result, "session_id": session_id}

        if intent.action == "video":
            result = MediaGenerationService.generate_video(request.message)
            response = result.get("message") if result.get("success") else result.get("error")
            memory_store.save_message(session_id, "assistant", response or "")
            return {"response": response, "intent": intent.action, "result": result, "session_id": session_id}

        if intent.action == "search":
            result = WebSearchService.detailed_search(request.message)
            response = result.get("summary", result.get("error", ""))
            memory_store.save_message(session_id, "assistant", response)
            return {"response": response, "intent": intent.action, "result": result, "session_id": session_id}

        response = engine.generate(

            "ollama",

            history_prompt,

            "qwen2.5:7b"
        )

        memory_store.save_message(session_id, "assistant", response)
        return {

            "response": response,

            "intent": intent.action,

            "session_id": session_id
        }

    except Exception as e:

        return {

            "error": str(e)
        }


def _with_history(prompt, history):
    turns = []
    for message in history[-30:]:
        role = "المستخدم" if message.get("role") == "user" else "المساعد"
        content = (message.get("content") or "").strip()
        if content:
            turns.append(f"{role}: {content}")
    if not turns:
        return prompt
    return "سياق المحادثة السابق:\n" + "\n".join(turns) + "\n\nالطلب الحالي:\n" + prompt
