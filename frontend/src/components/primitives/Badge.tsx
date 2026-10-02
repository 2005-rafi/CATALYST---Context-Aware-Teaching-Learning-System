'use client';

import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'neutral' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'sm',
  dot = false,
  className = '',
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center font-medium rounded-full border transition-colors select-none';

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-2',
  }[size];

  const variantClasses = {
    primary: 'bg-primary-container text-on-primary-container border-primary/20',
    secondary: 'bg-secondary-container text-on-secondary-container border-secondary/20',
    neutral: 'bg-surface-container text-on-surface-variant border-outline-variant',
    success: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    error: 'bg-error-container/20 text-error border-error/30',
  }[variant];

  const dotClasses = {
    primary: 'bg-primary',
    secondary: 'bg-secondary',
    neutral: 'bg-on-surface-variant',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    error: 'bg-error',
  }[variant];

  return (
    <span
      className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
      {...props}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dotClasses}`} />}
      {children}
    </span>
  );
};
