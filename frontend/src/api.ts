import type { Article, Analysis, PaginatedArticleResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export async function fetchHeadlines(
  category = "general",
  page = 1,
  pageSize = 10,
): Promise<PaginatedArticleResponse> {
  const params = new URLSearchParams({
    category,
    page: String(page),
    page_size: String(pageSize),
  });
  const res = await fetch(`${API_BASE}/news/headlines?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch headlines");
  }
  return res.json();
}

export async function searchNews(
  query: string,
  page = 1,
  pageSize = 10,
): Promise<PaginatedArticleResponse> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  const res = await fetch(`${API_BASE}/news?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch news");
  }
  return res.json();
}

export async function analyzeArticle(article: Article): Promise<Analysis> {
  const res = await fetch(`${API_BASE}/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ article }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to analyze article");
  }
  return res.json();
}

export async function fetchanalysis(): Promise<Analysis[]> {
  const res = await fetch(`${API_BASE}/analysis`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch analysis");
  }
  return res.json();
}

export async function deleteAnalysis(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/analysis/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to delete analysis");
  }
}
