'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled = false,
      icon,
      iconPosition = 'left',
      className = '',
      ...props
    },
    ref
  ) => {
    // Base layout: inline-flex, centered, transition, focus ring
    const baseClasses =
      'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus-visible:outline-2 focus-visible:outline-primary focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none';

    // Variant tokens mapped directly to Material 3 variables
    const variantClasses = {
      primary:
        'bg-primary text-primary-foreground hover:opacity-90 shadow-sm active:scale-[0.98]',
      secondary:
        'bg-secondary-container text-on-secondary-container hover:opacity-90 active:scale-[0.98]',
      outline:
        'border border-outline-variant bg-transparent text-on-surface hover:bg-surface-container-high active:scale-[0.98]',
      ghost:
        'bg-transparent text-on-surface hover:bg-surface-container active:scale-[0.98]',
      danger:
        'bg-error text-error-foreground hover:opacity-90 shadow-sm active:scale-[0.98]',
    }[variant];

    // Size tokens
    const sizeClasses = {
      sm: 'text-xs px-2.5 py-1.5 gap-1.5 min-h-[32px]',
      md: 'text-sm px-4 py-2 gap-2 min-h-[40px]',
      lg: 'text-base px-5 py-2.5 gap-2.5 min-h-[48px]',
    }[size];

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
        {...props}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
        ) : (
          icon && iconPosition === 'left' && <span className="flex-shrink-0">{icon}</span>
        )}
        <span>{children}</span>
        {!loading && icon && iconPosition === 'right' && (
          <span className="flex-shrink-0">{icon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
