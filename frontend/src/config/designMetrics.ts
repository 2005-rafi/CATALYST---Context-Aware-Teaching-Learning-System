/**
 * CATALYST Design System — Centralized Design Tokens & Layout Metrics
 * Reference: docs/DESIGN.md & docs/plan.md
 * SOLID & Production Grade Configuration
 */

export const LAYOUT_METRICS = {
  // Navigation & Sidebars
  MAIN_NAV_WIDTH: '15rem', // 240px
  SESSION_SIDEBAR_WIDTH: '16rem', // 256px
  SLIM_RAIL_WIDTH: '3.5rem', // 56px
  HEADER_HEIGHT: '3.75rem', // 60px
  
  // Reading & Editorial Canvases
  READING_MAX_WIDTH: '56rem', // 896px (max-w-4xl for comfortable readability)
  CANVAS_MAX_WIDTH: '64rem', // 1024px (max-w-5xl for wide tables & diagrams)
  ANALYTICS_MAX_WIDTH: '80rem', // 1280px (max-w-7xl for multi-column dashboards)
  
  // Z-Index Layers
  Z_INDEX: {
    FEED_BACKGROUND: 0,
    STICKY_HEADER: 20,
    DRAWER_BACKDROP: 40,
    DRAWER_SHEET: 50,
    MODAL_OVERLAY: 60,
    LIGHTBOX: 70,
    TOAST: 100,
  },
} as const;

export const SPACING_TOKENS = {
  containerPaddingX: 'px-4 sm:px-6 lg:px-8',
  containerPaddingY: 'py-6 sm:py-8',
  cardPadding: 'p-5 sm:p-6',
  cardPaddingCompact: 'p-3.5 sm:p-4',
  sectionGap: 'gap-6',
  itemGap: 'gap-3',
} as const;

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export const MOTION = {
  easeStandard: 'cubic-bezier(0.2, 0, 0, 1)',
  durationFast: '150ms',
  durationNormal: '250ms',
  durationSlow: '350ms',
} as const;

export const STREAMING_CONFIG = {
  defaultTokenIntervalMs: 18,
  batchSizeWords: 2,
  maxRevealDurationMs: 4000,
} as const;
