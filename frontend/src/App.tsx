import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Article, Analysis } from "./types";
import {
  fetchHeadlines,
  searchNews,
  analyzeArticle,
  fetchanalysis,
  deleteAnalysis,
} from "./api";
import SearchBar from "./components/SearchBar";
import ArticleCard from "./components/ArticleCard";
import AnalysisCard from "./components/AnalysisCard";

type Tab = "headlines" | "search" | "history";

export default function App() {
  const [headlines, setHeadlines] = useState<Article[]>([]);
  const [searchResults, setSearchResults] = useState<Article[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("headlines");
  const [query, setQuery] = useState("");
  const [loadingHeadlines, setLoadingHeadlines] = useState(false);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [analyzingUrl, setAnalyzingUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [headlinePage, setHeadlinePage] = useState(1);
  const [headlineTotalPages, setHeadlineTotalPages] = useState(1);
  const [searchPage, setSearchPage] = useState(1);
  const [searchTotalPages, setSearchTotalPages] = useState(1);
  const [searchTotal, setSearchTotal] = useState(0);

  useEffect(() => {
    loadHeadlines();
    loadAnalyses();
  }, []);

  const loadHeadlines = async (page = 1) => {
    setLoadingHeadlines(true);
    setError(null);
    try {
      const data = await fetchHeadlines("general", page);
      setHeadlines(data.articles);
      setHeadlinePage(data.page);
      setHeadlineTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load headlines");
    } finally {
      setLoadingHeadlines(false);
    }
  };

  const loadAnalyses = async () => {
    try {
      const data = await fetchanalysis();
      setAnalyses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    }
  };

  const handleSearch = async (q: string, page = 1) => {
    if (page === 1) {
      setQuery(q);
      setSearchPage(1);
    }
    setError(null);
    setLoadingSearch(true);
    setActiveTab("search");
    try {
      const data = await searchNews(q, page);
      setSearchResults(data.articles);
      setSearchPage(data.page);
      setSearchTotalPages(data.total_pages);
      setSearchTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleHeadlinePage = (page: number) => loadHeadlines(page);
  const handleSearchPage = (page: number) => handleSearch(query, page);

  const handleAnalyze = async (article: Article) => {
    setError(null);
    setAnalyzingUrl(article.url);
    try {
      const result = await analyzeArticle(article);
      setAnalyses((prev) => [
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
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const currentArticles = activeTab === "search" ? searchResults : headlines;
  const isLoadingArticles =
    activeTab === "search" ? loadingSearch : loadingHeadlines;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 px-4 py-4 backdrop-blur-sm">
        <div className="mx-auto max-w-4xl space-y-3">
          <div className="flex items-baseline gap-3">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              News Analyzer
            </h1>
            <span className="text-sm text-slate-400">
              AI summaries &amp; sentiment
            </span>
          </div>
          <SearchBar onSearch={handleSearch} loading={loadingSearch} />
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-6">
        {error && (
          <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Tab pills */}
        <div className="mb-6 flex w-fit items-center gap-1 rounded-xl bg-slate-100 p-1">
          <TabPill
            active={activeTab === "headlines"}
            onClick={() => setActiveTab("headlines")}
          >
            Headlines
          </TabPill>
          {query && (
            <TabPill
              active={activeTab === "search"}
              onClick={() => setActiveTab("search")}
            >
              Results
              {searchTotal > 0 && <Badge color="blue">{searchTotal}</Badge>}
            </TabPill>
          )}
          <TabPill
            active={activeTab === "history"}
            onClick={() => setActiveTab("history")}
          >
            History
            {analyses.length > 0 && (
              <Badge color="slate">{analyses.length}</Badge>
            )}
          </TabPill>
        </div>

        {/* Article grid */}
        {activeTab !== "history" &&
          (isLoadingArticles ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="h-52 animate-pulse rounded-xl bg-slate-200"
                />
              ))}
            </div>
          ) : currentArticles.length === 0 ? (
            <EmptyState>
              {activeTab === "headlines"
                ? "Could not load top headlines."
                : `No articles found for "${query}".`}
            </EmptyState>
          ) : (
            <>
              <div className="grid gap-4 sm:grid-cols-2">
                {currentArticles.map((article) => (
                  <ArticleCard
                    key={article.url}
                    article={article}
                    onAnalyze={handleAnalyze}
                    analyzing={analyzingUrl === article.url}
                  />
                ))}
              </div>
              <Pagination
                page={activeTab === "headlines" ? headlinePage : searchPage}
                totalPages={
                  activeTab === "headlines"
                    ? headlineTotalPages
                    : searchTotalPages
                }
                onPage={
                  activeTab === "headlines"
                    ? handleHeadlinePage
                    : handleSearchPage
                }
              />
            </>
          ))}

        {/* History grid */}
        {activeTab === "history" &&
          (analyses.length === 0 ? (
            <EmptyState>
              No analyses yet. Open an article and click Summarise.
            </EmptyState>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {analyses.map((item) => (
                <AnalysisCard
                  key={item.id}
                  analysis={item}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          ))}
      </main>
    </div>
  );
}

function TabPill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1 rounded-lg px-4 py-1.5 text-sm font-medium transition-colors ${
        active
          ? "bg-white text-slate-900 shadow-sm"
          : "text-slate-500 hover:text-slate-700"
      }`}
    >
      {children}
    </button>
  );
}

function Badge({
  color,
  children,
}: {
  color: "blue" | "slate";
  children: ReactNode;
}) {
  const styles =
    color === "blue"
      ? "bg-blue-100 text-blue-700"
      : "bg-slate-200 text-slate-600";
  return (
    <span
      className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold ${styles}`}
    >
      {children}
    </span>
  );
}

function Pagination({
  page,
  totalPages,
  onPage,
}: {
  page: number;
  totalPages: number;
  onPage: (p: number) => void;
}) {
  if (totalPages <= 1) return null;
  return (
    <div className="mt-6 flex items-center justify-center gap-3">
      <button
        disabled={page <= 1}
        onClick={() => onPage(page - 1)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
      >
        ← Prev
      </button>
      <span className="text-sm text-slate-500">
        Page {page} of {totalPages}
      </span>
      <button
        disabled={page >= totalPages}
        onClick={() => onPage(page + 1)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Next →
      </button>
    </div>
  );
}

function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white py-20 text-center text-sm text-slate-400">
      {children}
    </div>
  );
}
