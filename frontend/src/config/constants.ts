/**
 * Application-wide constants, health metrics, and polling intervals.
 */

export type HealthStatus = 'healthy' | 'operational' | 'degraded' | 'offline';

export const HEALTH_STATUS_CONFIG: Record<
  HealthStatus,
  {
    label: string;
    description: string;
    badgeClass: string;
    dotClass: string;
    isOnline: boolean;
  }
> = {
  healthy: {
    label: 'All Systems Operational',
    description: 'Core retrieval and all LLM providers are online.',
    badgeClass: 'text-primary bg-primary/10 border-primary/20',
    dotClass: 'bg-primary',
    isOnline: true,
  },
  operational: {
    label: 'Core Systems Operational',
    description: 'Vector and database systems are ready. LLM fallback available.',
    badgeClass: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
    dotClass: 'bg-emerald-500',
    isOnline: true,
  },
  degraded: {
    label: 'Degraded Performance',
    description: 'One or more subsystem dependencies are experiencing issues.',
    badgeClass: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    dotClass: 'bg-amber-500',
    isOnline: true,
  },
  offline: {
    label: 'Backend Disconnected',
    description: 'Unable to establish a connection with the server.',
    badgeClass: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
    dotClass: 'bg-rose-500 animate-ping',
    isOnline: false,
  },
};

export const POLLING_INTERVALS = {
  HEALTH_CHECK_MS: 30000,
  HEALTH_CHECK_RETRY_MS: 10000,
  DOCUMENT_INGESTION_MS: 3000,
  RETRY_BACKOFF_BASE_MS: 1000,
  MAX_RETRIES: 3,
} as const;

export const APP_CONFIG = {
  APP_NAME: 'CATALYST',
  APP_TAGLINE: 'Context-Aware Teaching & Learning System',
  VERSION: '2.0.0',
  DEFAULT_PAGE_SIZE: 20,
  MAX_UPLOAD_SIZE_BYTES: 50 * 1024 * 1024, // 50MB
  SUPPORTED_DOCUMENT_TYPES: [
    'application/pdf',
    'text/plain',
    'text/markdown',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  STORAGE_KEYS: {
    ACTIVE_WORKSPACE: 'catalyst_active_workspace',
    ACTIVE_SESSION: 'catalyst_active_session',
    THEME: 'catalyst_theme',
    SIDEBAR_COLLAPSED: 'catalyst_sidebar_collapsed',
  },
} as const;
