from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import news_router, analysis_router
from app.config import settings
from app.database import engine, Base
Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(news_router)
app.include_router(analysis_router)


@app.get("/")
def root():
    return {"message": "News Analyzer"}


@app.get("/health")
def health():
    return {"status": "ok"}
