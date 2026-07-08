# News Analyzer — Backend

A FastAPI service that fetches news from GNews, stores analyses in PostgreSQL, and uses OpenAI to summarise articles and classify their sentiment.

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI + Uvicorn |
| Database | PostgreSQL via SQLAlchemy 2 |
| Validation | Pydantic v2 + pydantic-settings |
| AI | OpenAI (`gpt-4.1-nano` by default) |
| News data | GNews API |
| HTTP client | httpx |
| Testing | pytest |
| Container | Docker |

## Running locally

### Prerequisites
- Python 3.11+
- A running PostgreSQL instance
- A [GNews API key](https://gnews.io/) and an [OpenAI API key](https://platform.openai.com/)

### 1. Set up the environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/news_analyzer
GNEWS_API_KEY=your_gnews_key
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-nano
CORS_ORIGINS=http://localhost:5173
```

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running with Docker

```bash
docker build -t news-analyzer-backend .
docker run -p 8000:8000 --env-file .env news-analyzer-backend
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

## API overview

| Method | Path | What it does |
|---|---|---|
| `GET` | `/news/headlines` | Top headlines (paginated) |
| `GET` | `/news/search` | Search news by query |
| `POST` | `/analysis` | Analyse an article with OpenAI |
| `GET` | `/analysis` | List past analyses |
| `DELETE` | `/analysis/{id}` | Delete an analysis |
| `GET` | `/health` | Health check |
