'use client';

import React from 'react';

export interface MetricCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  className?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  icon,
  trend,
  className = '',
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={`relative overflow-hidden rounded-xl border border-border/70 bg-card/60 p-5 backdrop-blur-md transition-all duration-200 hover:border-border hover:shadow-md ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1.5 min-w-0">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground truncate">
            {label}
          </p>
          <div className="text-2xl font-bold tracking-tight text-foreground truncate">
            {value}
          </div>
          {subtitle && (
            <p className="text-xs text-muted-foreground truncate">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
            {icon}
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-3 flex items-center gap-1.5 text-xs font-medium">
          <span
            className={
              trend.isPositive !== false
                ? 'text-emerald-500 dark:text-emerald-400'
                : 'text-rose-500 dark:text-rose-400'
            }
          >
            {trend.value}
          </span>
          <span className="text-muted-foreground">vs previous</span>
        </div>
      )}
    </div>
  );
};
