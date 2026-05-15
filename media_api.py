from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core.intent import IntentClassifier
from core.media import MediaGenerationService, ModelProviderRegistry


router = APIRouter(prefix="/media", tags=["media"])


class IntentRequest(BaseModel):
    message: str


class ProviderRequest(BaseModel):
    media_type: str
    provider_id: str
    provider: Dict[str, Any]


class GenerationRequest(BaseModel):
    prompt: str
    provider_id: Optional[str] = None
    options: Dict[str, Any] = {}


@router.post("/intent")
def detect_intent(request: IntentRequest):
    return IntentClassifier.as_dict(request.message)


@router.get("/providers")
def providers():
    return ModelProviderRegistry.list_providers()


@router.post("/providers")
def add_provider(request: ProviderRequest):
    return ModelProviderRegistry.add_provider(
        request.media_type,
        request.provider_id,
        request.provider,
    )


@router.post("/generate-image")
def generate_image(request: GenerationRequest):
    return MediaGenerationService.generate_image(
        request.prompt,
        provider_id=request.provider_id,
        **request.options,
    )


@router.post("/generate-video")
def generate_video(request: GenerationRequest):
    return MediaGenerationService.generate_video(
        request.prompt,
        provider_id=request.provider_id,
        **request.options,
    )
