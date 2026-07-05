from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.repositories.analysis import AnalysisRepository
from app.schemas import AnalyzeRequest, AnalysisResponse
from app.services.openai import analyze_article

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def get_analysis_repository(db: Session = Depends(get_db)) -> AnalysisRepository:
    return AnalysisRepository(db)


def analyze(req: AnalyzeRequest,
            repo: AnalysisRepository = Depends(get_analysis_repository)):
    existing = repo.get_by_url(req.article.url)
    if existing:
        return existing

    try:
        ai_result = analyze_article(req.article)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"OpenAI API error: {str(exc)}")

    return repo.create(req.article, ai_result["summary"], ai_result["sentiment"])


@router.get("", response_model=List[AnalysisResponse])
def list_analysis(repo: AnalysisRepository = Depends(get_analysis_repository)):
    return repo.list_all()


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    repo: AnalysisRepository = Depends(get_analysis_repository)
):
    analysis = repo.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    repo.delete(analysis)
    return {"message": "Analysis deleted"}
