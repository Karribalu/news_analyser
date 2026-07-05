export interface Article {
  title: string;
  description?: string;
  content?: string;
  image?: string;
  url: string;
  source?: string;
  published_at?: string;
}

export interface Analysis {
  id: number;
  article_url: string;
  article_title: string;
  article_description?: string;
  article_image?: string;
  article_source?: string;
  article_published_at?: string;
  summary: string;
  sentiment: "positive" | "neutral" | "negative";
  created_at: string;
}
