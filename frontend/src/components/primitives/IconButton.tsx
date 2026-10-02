'use client';

import React from 'react';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'ghost' | 'surface' | 'primary' | 'danger';
  active?: boolean;
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      label,
      children,
      size = 'md',
      variant = 'ghost',
      active = false,
      disabled = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseClasses =
      'inline-flex items-center justify-center rounded-lg transition-all duration-200 focus-visible:outline-2 focus-visible:outline-primary focus-visible:outline-offset-2 disabled:opacity-40 disabled:cursor-not-allowed select-none flex-shrink-0';

    const sizeClasses = {
      sm: 'w-8 h-8 text-xs',
      md: 'w-10 h-10 text-sm',
      lg: 'w-12 h-12 text-base',
    }[size];

    const variantClasses = {
      ghost: active
        ? 'bg-primary-container text-on-primary-container font-medium'
        : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface',
      surface: active
        ? 'bg-primary-container text-on-primary-container'
        : 'bg-surface-container border border-outline-variant text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high',
      primary: 'bg-primary text-primary-foreground hover:opacity-90 shadow-sm',
      danger: 'text-error hover:bg-error-container/20 active:bg-error-container/30',
    }[variant];

    return (
      <button
        ref={ref}
        type="button"
        title={label}
        aria-label={label}
        disabled={disabled}
        className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

IconButton.displayName = 'IconButton';
