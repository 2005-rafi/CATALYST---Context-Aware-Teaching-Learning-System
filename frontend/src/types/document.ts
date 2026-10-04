/**
 * Document & Ingestion Data Models and Types
 */

export interface DocumentStatus {
  document_id: string;
  workspace_id: string;
  file_name: string;
  file_size_mb: number;
  total_chunks: number;
  processing_status: string;
  embedding_status: boolean;
  created_at: string;
}

export interface DocumentListResult {
  documents: DocumentStatus[];
  count: number;
}

export interface DocumentUploadResponse {
  success: boolean;
  document_id: string;
  message: string;
}
