/**
 * Analytics, Topic Intelligence & Mastery Types
 */

import { FigureMetricSummary } from './figure';

export interface AnalyticsResult {
  last_updated?: string;
  total_queries?: number;
  total_documents?: number;
  total_chunks?: number;
  storage_used_mb?: number;
  groq_requests?: number;
  local_model_requests?: number;
}

export interface DailyActivityPoint {
  date: string;
  label: string;
  query_count: number;
  message_count: number;
}

export interface TopicMasteryItem {
  topic: string;
  familiarity_score: number;
  familiarity_percent: number;
  level: string;
  query_count: number;
  is_struggling: boolean;
}

export interface DocumentMetricItem {
  document_id: string;
  file_name: string;
  file_type: string;
  file_size_mb: number;
  total_chunks: number;
  figures_count: number;
  upload_time: string;
  processing_status: string;
}

export interface DetailedAnalyticsResult {
  workspace_id: string;
  workspace_name: string;
  created_at: string;
  last_updated?: string;
  total_queries: number;
  total_documents: number;
  total_chunks: number;
  storage_used_mb: number;
  groq_requests: number;
  local_model_requests: number;
  avg_chunks_per_query: number;
  total_sessions: number;
  total_messages: number;
  learning_style: string;
  preferred_mode: string;
  topic_mastery: TopicMasteryItem[];
  struggle_topics: string[];
  activity_timeline: DailyActivityPoint[];
  documents: DocumentMetricItem[];
  figures_summary: FigureMetricSummary;
}
