/**
 * Core API, System Health & Network Types
 */

export interface SystemHealthResult {
  status: string;
  version: string;
  subsystems: Record<string, { status: string; detail?: string }>;
}

export interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}
