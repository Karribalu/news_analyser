# News Analyzer — Frontend

A React app for browsing top headlines, searching the news, and reading AI-generated summaries with sentiment scores. Talks to the FastAPI backend.

## Tech Stack

| Layer | Choice |
|---|---|
| UI library | React 18 |
| Language | TypeScript |
| Bundler | Vite |
| Styling | Tailwind CSS |
| Linting | ESLint + typescript-eslint |

## Running locally

### Prerequisites
- Node.js 18+
- The backend running at `http://localhost:8000`

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start the dev server

```bash
npm run dev
```

Opens at `http://localhost:5173` by default.

### Other commands

```bash
npm run build    # production build → dist/
npm run preview  # preview the production build locally
npm run lint     # run ESLint
```

## Features

- **Headlines** — pulls top news on load, paginated
- **Search** — search by keyword across the GNews index
- **History** — view and delete past AI analyses
- **Analyse** — click any article to get an OpenAI summary + sentiment tag
