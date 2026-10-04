/**
 * Centralized API Endpoint Registry
 * All backend API routes must be referenced through this registry.
 * Robust normalization ensures compatibility across local and production (Vercel/Render/Fly.io).
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
  FIGURES: {
    BY_WORKSPACE: (workspaceId: string) => `/figures/workspace/${encodeURIComponent(workspaceId)}`,
    DETAIL: (figureId: string) => `/figures/${encodeURIComponent(figureId)}`,
    PREVIEW: (figureId: string) => `/figures/${encodeURIComponent(figureId)}/preview`,
  },
  CHAT: {
    SEND: '/chat/',
    HISTORY: (workspaceId: string, sessionId?: string) => {
      const base = `/chat/history/${encodeURIComponent(workspaceId)}`;
      return sessionId ? `${base}?session_id=${encodeURIComponent(sessionId)}` : base;
    },
  },
  ANALYTICS: {
    BY_WORKSPACE: (workspaceId: string) => `/analytics/${encodeURIComponent(workspaceId)}`,
    DETAILED: (workspaceId: string, days: number = 14) =>
      `/analytics/${encodeURIComponent(workspaceId)}/detailed?days=${days}`,
  },
  // --- Conversational Intelligence ---
  SESSIONS: {
    LIST: (workspaceId: string) => `/session/workspace/${encodeURIComponent(workspaceId)}`,
    CREATE: (workspaceId: string) => `/session/workspace/${encodeURIComponent(workspaceId)}`,
    DETAIL: (sessionId: string) => `/session/${encodeURIComponent(sessionId)}`,
    RENAME: (sessionId: string) => `/session/${encodeURIComponent(sessionId)}`,
    ACTIVATE: (sessionId: string, workspaceId: string) =>
      `/session/${encodeURIComponent(sessionId)}/activate?workspace_id=${encodeURIComponent(workspaceId)}`,
    DELETE: (sessionId: string) => `/session/${encodeURIComponent(sessionId)}`,
  },
  MEMORY: {
    PROFILE: (workspaceId: string) => `/memory/workspace/${encodeURIComponent(workspaceId)}/profile`,
    RESET_PROFILE: (workspaceId: string) => `/memory/workspace/${encodeURIComponent(workspaceId)}/profile`,
  },
} as const;
