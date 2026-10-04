/**
 * Legacy API Re-export Layer
 * Maintains 100% backward compatibility for all imports from '@/lib/api'
 * Directs to modular services under '@/services/api' and types under '@/types'.
 */

export * from '@/types';
export * from '@/services/api';
