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
    <div className="group flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md overflow-hidden">
      {article.image && (
        <img
          src={article.image}
          alt={article.title}
          className="h-44 w-full object-cover"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = "none";
          }}
        />
      )}
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-1 flex items-center gap-1.5 text-xs text-slate-400">
          {article.source && (
            <span className="font-medium text-slate-500">{article.source}</span>
          )}
          {article.source && article.published_at && <span>·</span>}
          {article.published_at && (
            <span>
              {new Date(article.published_at).toLocaleDateString(undefined, {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>
          )}
        </div>
        <h3 className="mb-2 flex-1 text-sm font-semibold leading-snug text-slate-800 group-hover:text-blue-700">
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        </h3>
        {article.description && (
          <p className="mb-4 line-clamp-2 text-xs text-slate-500">
            {article.description}
          </p>
        )}
        <button
          onClick={() => onAnalyze(article)}
          disabled={analyzing}
          className="mt-auto rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-xs font-medium text-emerald-700 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {analyzing ? "Analysing…" : "Summarise & Analyse"}
        </button>
      </div>
    </div>
  );
}
