/**
 * Workspace Data Models and Types
 */

export interface WorkspaceSummary {
  workspace_id: string;
  workspace_name: string;
  description?: string;
  total_documents: number;
  total_chunks: number;
  created_at?: string;
}

export interface WorkspaceListResult {
  workspaces: WorkspaceSummary[];
  count: number;
}

export interface WorkspaceResult {
  workspace_id: string;
  workspace_name: string;
  description?: string;
  total_documents?: number;
  total_chunks?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkspacePayload {
  name: string;
  description?: string;
}
