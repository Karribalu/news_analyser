from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class Sentiment(str, Enum):
    Positive = "positive"
    Neutral = "neutral"
    Negative = "negative"


class Article(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    max_results: int = Field(10, ge=1, le=20)


class SearchResponse(BaseModel):
    articles: list[Article]


class PaginatedArticleResponse(BaseModel):
    articles: list[Article]
    total: int
    page: int
    page_size: int
    total_pages: int


class AnalyzeRequest(BaseModel):
    article: Article


class AnalysisResponse(BaseModel):
    id: int
    article_url: str
    article_title: str
    article_description: Optional[str]
    article_image: Optional[str]
    article_source: Optional[str]
    article_published_at: Optional[str]
    summary: str
    sentiment: Sentiment
    created_at: datetime

    class Config:
        from_attributes = True
