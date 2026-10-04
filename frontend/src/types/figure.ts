/**
 * Figure & Visual RAG Data Models and Types
 */

export interface FigureReference {
  figure_id: string;
  caption: string;
  figure_type: string;
  page_number: number;
  document_name: string;
  url: string;
}

export interface FigureMetricSummary {
  total_figures: number;
  by_type: Record<string, number>;
  sample_captions: string[];
}
