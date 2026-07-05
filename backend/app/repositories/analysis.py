from sqlalchemy.orm import Session

from app.models import Analysis
from app.schemas import Article, Sentiment


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_url(self, url: str) -> Analysis | None:
        return self.db.query(Analysis).filter(Analysis.article_url == url).first()

    def get_by_id(self, analysis_id: str) -> Analysis | None:
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def list_all(self, analysis_id: str) -> list[Analysis]:
        return self.db.query(Analysis).order_by(Analysis.created_at.desc()).all()

    def create(self, article: Article, summary: str, sentiment: Sentiment) -> Analysis:
        analysis = Analysis(
            article_url=article.url,
            article_title=article.title,
            article_description=article.description,
            article_source=article.source,
            article_published_at=article.published_at,
            summary=summary,
            sentiment=sentiment
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def delete(self, analysis: Analysis) -> None:
        self.db.delete(analysis)
        self.db.commit()
