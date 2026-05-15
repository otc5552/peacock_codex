from fastapi import APIRouter
from pydantic import BaseModel

from core.search import WebSearchService


router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    max_results: int = 6


@router.post("")
def search(request: SearchRequest):
    return WebSearchService.detailed_search(request.query, request.max_results)
