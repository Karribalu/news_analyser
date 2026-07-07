import type { Article, Analysis } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function fetchHeadlines(category = "general"): Promise<Article[]> {
  const res = await fetch(`${API_BASE}/news/headlines?category=${category}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch headlines");
  }
  const data = await res.json();
  return data.articles;
}

export async function searchNews(
  query: string,
  maxResults = 10,
): Promise<Article[]> {
  const params = new URLSearchParams({
    q: query,
    max_results: String(maxResults),
  });
  const res = await fetch(`${API_BASE}/news?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch news");
  }
  const data = await res.json();
  return data.articles;
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
