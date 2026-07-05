import { useEffect, useState } from "react";
import type { Article, Analysis } from "./types";
import {
  searchNews,
  analyzeArticle,
  fetchanalysis,
  deleteAnalysis,
} from "./api";
import SearchBar from "./components/SearchBar";
import ArticleCard from "./components/ArticleCard";
import AnalysisCard from "./components/AnalysisCard";

export default function App() {
  const [query, setQuery] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [analysis, setanalysis] = useState<Analysis[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [analyzingUrl, setAnalyzingUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"search" | "history">("search");

  useEffect(() => {
    loadanalysis();
  }, []);

  const loadanalysis = async () => {
    try {
      const data = await fetchanalysis();
      setanalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    }
  };

  const handleSearch = async (q: string) => {
    setQuery(q);
    setError(null);
    setLoadingSearch(true);
    try {
      const data = await searchNews(q);
      setArticles(data);
      setActiveTab("search");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleAnalyze = async (article: Article) => {
    setError(null);
    setAnalyzingUrl(article.url);
    try {
      const result = await analyzeArticle(article);
      setanalysis((prev) => [
        result,
        ...prev.filter((a) => a.id !== result.id),
      ]);
      setActiveTab("history");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzingUrl(null);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAnalysis(id);
      setanalysis((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-slate-900">News Analyzer</h1>
        <p className="mt-2 text-slate-600">
          Search the latest news, get AI summaries, and track sentiment.
        </p>
      </header>

      <div className="mb-6">
        <SearchBar onSearch={handleSearch} loading={loadingSearch} />
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800">
          {error}
        </div>
      )}

      <div className="mb-6 flex gap-4 border-b border-slate-200">
        <button
          onClick={() => setActiveTab("search")}
          className={`pb-2 text-sm font-medium ${
            activeTab === "search"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Search Results {articles.length > 0 && `(${articles.length})`}
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`pb-2 text-sm font-medium ${
            activeTab === "history"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Analysis History {analysis.length > 0 && `(${analysis.length})`}
        </button>
      </div>

      {activeTab === "search" && (
        <section>
          {!query && articles.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 py-16 text-center text-slate-500">
              Enter a topic above to find recent news articles.
            </div>
          )}
          {query && articles.length === 0 && !loadingSearch && (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 py-16 text-center text-slate-500">
              No articles found for “{query}”.
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {articles.map((article) => (
              <ArticleCard
                key={article.url}
                article={article}
                onAnalyze={handleAnalyze}
                analyzing={analyzingUrl === article.url}
              />
            ))}
          </div>
        </section>
      )}

      {activeTab === "history" && (
        <section>
          {analysis.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 py-16 text-center text-slate-500">
              No analysis yet. Search for an article and analyze one to get
              started.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {analysis.map((analysis) => (
                <AnalysisCard
                  key={analysis.id}
                  analysis={analysis}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
