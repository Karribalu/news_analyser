import type { Analysis } from "../types";

interface AnalysisCardProps {
  analysis: Analysis;
  onDelete: (id: number) => void;
}

const sentimentStyles = {
  positive: "bg-green-100 text-green-800 border-green-200",
  neutral: "bg-slate-100 text-slate-800 border-slate-200",
  negative: "bg-red-100 text-red-800 border-red-200",
};

export default function AnalysisCard({
  analysis,
  onDelete,
}: AnalysisCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between gap-4">
        <h3 className="text-lg font-semibold leading-snug text-slate-800">
          <a
            href={analysis.article_url}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            {analysis.article_title}
          </a>
        </h3>
        <span
          className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
            sentimentStyles[analysis.sentiment] || sentimentStyles.neutral
          }`}
        >
          {analysis.sentiment}
        </span>
      </div>
      <p className="mb-4 text-sm text-slate-700">{analysis.summary}</p>
      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-3">
          {analysis.article_source && (
            <span className="rounded-full bg-slate-100 px-2 py-1">
              {analysis.article_source}
            </span>
          )}
          <span>{new Date(analysis.created_at).toLocaleString()}</span>
        </div>
        <button
          onClick={() => onDelete(analysis.id)}
          className="text-red-600 hover:text-red-800 hover:underline"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
