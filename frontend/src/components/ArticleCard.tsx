import type { Article } from "../types";

interface ArticleCardProps {
  article: Article;
  onAnalyze: (article: Article) => void;
  analyzing: boolean;
}

export default function ArticleCard({
  article,
  onAnalyze,
  analyzing,
}: ArticleCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="mb-2 flex items-start justify-between gap-4">
        <h3 className="text-lg font-semibold leading-snug text-slate-800">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            {article.title}
          </a>
        </h3>
      </div>
      <p className="mb-3 line-clamp-3 text-sm text-slate-600">
        {article.description || "No description available."}
      </p>
      <div className="mb-4 flex items-center gap-3 text-xs text-slate-500">
        {article.source && (
          <span className="rounded-full bg-slate-100 px-2 py-1">
            {article.source}
          </span>
        )}
        {article.published_at && (
          <span>{new Date(article.published_at).toLocaleString()}</span>
        )}
      </div>
      <button
        onClick={() => onAnalyze(article)}
        disabled={analyzing}
        className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300"
      >
        {analyzing ? "Analyzing..." : "Summarize & Analyze Sentiment"}
      </button>
    </div>
  );
}
