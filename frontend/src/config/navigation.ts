/**
 * Centralized Navigation Routes and Tab Configurations
 * Provides type-safe route generation and unified navigation structures across all pages and sidebars.
 */

export const ROUTES = {
  HOME: '/',
  WORKSPACE: (workspaceId: string) => `/workspaces/${encodeURIComponent(workspaceId)}`,
  CHAT: (workspaceId: string, sessionId?: string) => {
    const base = `/workspaces/${encodeURIComponent(workspaceId)}/chat`;
    return sessionId ? `${base}?session_id=${encodeURIComponent(sessionId)}` : base;
  },
  DOCUMENTS: (workspaceId: string) => `/workspaces/${encodeURIComponent(workspaceId)}/documents`,
  ANALYTICS: (workspaceId: string) => `/workspaces/${encodeURIComponent(workspaceId)}/analytics`,
} as const;

export interface WorkspaceTabItem {
  id: 'chat' | 'documents' | 'analytics';
  label: string;
  iconName: 'chat' | 'document' | 'chart';
  getHref: (workspaceId: string) => string;
}

export const WORKSPACE_NAV_TABS: WorkspaceTabItem[] = [
  {
    id: 'chat',
    label: 'Chat Session',
    iconName: 'chat',
    getHref: (workspaceId: string) => ROUTES.CHAT(workspaceId),
  },
  {
    id: 'documents',
    label: 'Knowledge Base',
    iconName: 'document',
    getHref: (workspaceId: string) => ROUTES.DOCUMENTS(workspaceId),
  },
  {
    id: 'analytics',
    label: 'Analytics & Mastery',
    iconName: 'chart',
    getHref: (workspaceId: string) => ROUTES.ANALYTICS(workspaceId),
  },
];
