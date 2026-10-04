/**
 * Unified HTTP API Client with Retry Backoff & Error Handling
 * Adheres to SOLID Single Responsibility Principle for network communication.
 */

import { API_BASE_URL } from '@/config/endpoints';
import { POLLING_INTERVALS } from '@/config/constants';
import { FetchOptions } from '@/types/api';

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

async function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchWrapper<T = unknown>(
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
          errorDetail =
            (errorData.detail as string) ||
            (errorData.error as string) ||
            (errorData.message as string) ||
            errorDetail;
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
        `Unable to connect to the backend server at ${API_BASE_URL}. Please verify the backend service is online.`,
        503,
        { originalError: err.message },
        undefined,
        true
      );
    }
  }

  throw lastError ?? new Error('Unknown fetch failure');
}
