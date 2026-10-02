'use client';

import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'flat' | 'raised' | 'interactive';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      variant = 'flat',
      padding = 'md',
      className = '',
      ...props
    },
    ref
  ) => {
    const baseClasses =
      'rounded-xl border border-outline-variant bg-surface-container-low transition-all duration-200';

    const variantClasses = {
      flat: 'shadow-none',
      raised: 'bg-surface-container shadow-sm hover:shadow-md',
      interactive:
        'hover:border-outline hover:bg-surface-container cursor-pointer active:scale-[0.99]',
    }[variant];

    const paddingClasses = {
      none: 'p-0',
      sm: 'p-3',
      md: 'p-5',
      lg: 'p-6',
    }[padding];

    return (
      <div
        ref={ref}
        className={`${baseClasses} ${variantClasses} ${paddingClasses} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';
