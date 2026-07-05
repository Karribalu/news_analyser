import type { Analysis } from "../types";

interface AnalysisCardProps {
  analysis: Analysis;
  onDelete: (id: number) => void;
}

const sentimentConfig: Record<string, { badge: string; dot: string }> = {
  positive: {
    badge: "bg-green-50 text-green-700 border-green-200",
    dot: "bg-green-500",
  },
  neutral: {
    badge: "bg-slate-100 text-slate-600 border-slate-200",
    dot: "bg-slate-400",
  },
  negative: {
    badge: "bg-red-50 text-red-700 border-red-200",
    dot: "bg-red-500",
  },
};

export default function AnalysisCard({
  analysis,
  onDelete,
}: AnalysisCardProps) {
  const config = sentimentConfig[analysis.sentiment] ?? sentimentConfig.neutral;

  return (
    <div className="flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {analysis.article_image && (
        <img
          src={analysis.article_image}
          alt={analysis.article_title}
          className="h-40 w-full object-cover"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = "none";
          }}
        />
      )}
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-3 flex items-start justify-between gap-3">
          <h3 className="text-sm font-semibold leading-snug text-slate-800">
            <a
              href={analysis.article_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-700"
            >
              {analysis.article_title}
            </a>
          </h3>
          <span
            className={`flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium capitalize ${config.badge}`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
            {analysis.sentiment}
          </span>
        </div>
        <p className="mb-4 flex-1 text-sm leading-relaxed text-slate-600">
          {analysis.summary}
        </p>
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            {analysis.article_source && (
              <span className="font-medium text-slate-500">
                {analysis.article_source}
              </span>
            )}
            <span>{new Date(analysis.created_at).toLocaleDateString()}</span>
          </div>
          <button
            onClick={() => onDelete(analysis.id)}
            className="transition-colors hover:text-red-600"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
