'use client';

import React from 'react';

export type StatusVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

export interface StatusBadgeProps {
  status: string;
  variant?: StatusVariant;
  showDot?: boolean;
  className?: string;
}

const VARIANT_MAP: Record<StatusVariant, { bg: string; text: string; border: string; dot: string }> = {
  success: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-500 dark:text-emerald-400',
    border: 'border-emerald-500/20',
    dot: 'bg-emerald-500',
  },
  warning: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-500 dark:text-amber-400',
    border: 'border-amber-500/20',
    dot: 'bg-amber-500',
  },
  error: {
    bg: 'bg-rose-500/10',
    text: 'text-rose-500 dark:text-rose-400',
    border: 'border-rose-500/20',
    dot: 'bg-rose-500',
  },
  info: {
    bg: 'bg-primary/10',
    text: 'text-primary',
    border: 'border-primary/20',
    dot: 'bg-primary',
  },
  neutral: {
    bg: 'bg-muted/50',
    text: 'text-muted-foreground',
    border: 'border-border/60',
    dot: 'bg-muted-foreground',
  },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  variant = 'neutral',
  showDot = true,
  className = '',
}) => {
  const styles = VARIANT_MAP[variant] || VARIANT_MAP.neutral;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border ${styles.bg} ${styles.text} ${styles.border} ${className}`}
    >
      {showDot && <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} />}
      {status}
    </span>
  );
};
