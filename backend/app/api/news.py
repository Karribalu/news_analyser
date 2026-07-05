from fastapi import APIRouter, HTTPException, Query

from app.schemas import SearchResponse
from app.services.news import fetch_articles

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=SearchResponse)
def search_news(
    q: str = Query(..., min_length=1, max_length=200),
    max_results: int = Query(10, ge=1, le=20)
):
    try:
        articles = fetch_articles(q, max_results)
        return SearchResponse(articles=articles)

    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"News API error: {str(exc)}")
