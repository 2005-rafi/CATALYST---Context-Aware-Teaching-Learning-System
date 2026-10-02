import { API_BASE_URL, ENDPOINTS } from './endpoints';
import { POLLING_INTERVALS } from './constants';

export class APIError extends Error {
  public status: number;
  public details: unknown;
  public requestId?: string;
  public isNetworkError: boolean;

  constructor(
    message: string,
    status: number,
    details?: unknown,
    requestId?: string,
    isNetworkError: boolean = false
  ) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
    this.requestId = requestId;
    this.isNetworkError = isNetworkError;
  }
}

interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}

async function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWrapper<T = unknown>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const maxRetries = options.retries ?? 0;
  const retryDelay = options.retryDelay ?? POLLING_INTERVALS.RETRY_BACKOFF_BASE_MS;

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Only add Content-Type if we're sending a JSON string body
  if (options.body && typeof options.body === 'string') {
    headers['Content-Type'] = 'application/json';
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const requestId = response.headers.get('X-Request-ID') || undefined;

      if (!response.ok) {
        let errorDetail = `Request failed with status ${response.status}`;
        let details: unknown = null;
        try {
          const errorData = (await response.json()) as Record<string, unknown>;
          errorDetail = (errorData.detail as string) || (errorData.error as string) || (errorData.message as string) || errorDetail;
          details = errorData;
        } catch {
          errorDetail = await response.text();
        }
        throw new APIError(errorDetail, response.status, details, requestId, false);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return null as unknown as T;
      }

      return (await response.json()) as T;
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      lastError = err;

      if (err instanceof APIError && !err.isNetworkError) {
        if (err.status !== 503 || attempt === maxRetries) {
          throw err;
        }
      }

      // Retry backoff
      if (attempt < maxRetries) {
        const backoff = retryDelay * Math.pow(2, attempt);
        await wait(backoff);
        continue;
      }

      if (err instanceof APIError) {
        throw err;
      }

      throw new APIError(
        'Unable to connect to the backend server. Please verify the backend service is running on port 8000.',
        503,
        { originalError: err.message },
        undefined,
        true
      );
    }
  }

  throw lastError ?? new Error('Unknown fetch failure');
}

// ---------------------------------------------------------------------------
// Typed API Endpoints
// ---------------------------------------------------------------------------
export interface WorkspaceListResult {
  workspaces: Array<{
    workspace_id: string;
    workspace_name: string;
    description?: string;
    total_documents: number;
    total_chunks: number;
    created_at?: string;
  }>;
  count: number;
}

export interface WorkspaceResult {
  workspace_id: string;
  workspace_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

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

export interface ChatResponse {
  response: string;
  model_used: string;
  sources?: Array<{ file_name: string; chunk_count: number }>;
}

export interface SystemHealthResult {
  status: string;
  version: string;
  subsystems: Record<string, { status: string; detail?: string }>;
}

export interface AnalyticsResult {
  last_updated?: string;
  total_queries?: number;
  total_documents?: number;
  total_chunks?: number;
  storage_used_mb?: number;
  groq_requests?: number;
  local_model_requests?: number;
}

export const getWorkspaces = () => 
  fetchWrapper<WorkspaceListResult>(ENDPOINTS.WORKSPACES.LIST, { retries: 1 });

export const getWorkspace = (id: string) => 
  fetchWrapper<WorkspaceResult>(ENDPOINTS.WORKSPACES.DETAIL(id));

export const createWorkspace = (data: { name: string; description?: string }) =>
  fetchWrapper<WorkspaceResult>(ENDPOINTS.WORKSPACES.CREATE, {
    method: 'POST',
    body: JSON.stringify({ workspace_name: data.name, description: data.description }),
  });

export const deleteWorkspace = (id: string) =>
  fetchWrapper<null>(ENDPOINTS.WORKSPACES.DELETE(id), { method: 'DELETE' });

export const getDocumentsByWorkspace = (workspaceId: string) =>
  fetchWrapper<DocumentListResult>(ENDPOINTS.DOCUMENTS.BY_WORKSPACE(workspaceId));

export const uploadDocument = (workspaceId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('workspace_id', workspaceId);
  return fetchWrapper<{ success: boolean; document_id: string; message: string }>(ENDPOINTS.DOCUMENTS.UPLOAD, {
    method: 'POST',
    body: formData,
  });
};

export const deleteDocument = (id: string) =>
  fetchWrapper<null>(ENDPOINTS.DOCUMENTS.DELETE(id), { method: 'DELETE' });

export const sendMessage = (workspaceId: string, query: string, mode: string = 'medium') =>
  fetchWrapper<ChatResponse>(ENDPOINTS.CHAT.SEND, {
    method: 'POST',
    body: JSON.stringify({ workspace_id: workspaceId, query, model: mode }),
  });

export const getChatHistory = (workspaceId: string) =>
  fetchWrapper<Array<{
    id?: string;
    role: string;
    message: string;
    model_used?: string;
    created_at?: string;
  }>>(ENDPOINTS.CHAT.HISTORY(workspaceId));

export const getAnalytics = (workspaceId: string) =>
  fetchWrapper<AnalyticsResult>(ENDPOINTS.ANALYTICS.BY_WORKSPACE(workspaceId));

export const getSystemHealth = () => 
  fetchWrapper<SystemHealthResult>(ENDPOINTS.SYSTEM.HEALTH);
