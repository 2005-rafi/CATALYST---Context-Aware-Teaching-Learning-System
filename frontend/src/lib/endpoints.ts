/**
 * Centralized API Endpoint Registry
 * All backend API routes must be referenced through this registry.
 * Robust normalization ensures compatibility across local and production (Vercel/Render).
 */

const rawBase = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').trim().replace(/\/+$/, '');
export const API_BASE_URL = rawBase.endsWith('/api/v1') ? rawBase : `${rawBase}/api/v1`;

export const ENDPOINTS = {
  SYSTEM: {
    HEALTH: '/system/health',
    ROOT: '/',
  },
  WORKSPACES: {
    LIST: '/workspace/',
    CREATE: '/workspace/',
    DETAIL: (id: string) => `/workspace/${encodeURIComponent(id)}`,
    DELETE: (id: string) => `/workspace/${encodeURIComponent(id)}`,
  },
  DOCUMENTS: {
    BY_WORKSPACE: (workspaceId: string) => `/document/workspace/${encodeURIComponent(workspaceId)}`,
    UPLOAD: '/document/upload',
    DELETE: (id: string) => `/document/${encodeURIComponent(id)}`,
  },
  CHAT: {
    SEND: '/chat/',
    HISTORY: (workspaceId: string) => `/chat/history/${encodeURIComponent(workspaceId)}`,
  },
  ANALYTICS: {
    BY_WORKSPACE: (workspaceId: string) => `/analytics/${encodeURIComponent(workspaceId)}`,
  },
} as const;
