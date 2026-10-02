'use client';

import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
  iconPrefix?: React.ReactNode;
  iconSuffix?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error,
      iconPrefix,
      iconSuffix,
      id,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || React.useId();

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-medium text-on-surface select-none tracking-wide"
          >
            {label}
          </label>
        )}

        <div className="relative flex items-center">
          {iconPrefix && (
            <div className="absolute left-3 text-on-surface-variant pointer-events-none flex items-center justify-center">
              {iconPrefix}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            disabled={disabled}
            aria-invalid={!!error}
            aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
            className={`w-full bg-surface-container-low border text-on-surface text-sm rounded-lg px-3.5 py-2.5 transition-all duration-200 placeholder:text-on-surface-variant/60 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed ${
              iconPrefix ? 'pl-10' : ''
            } ${iconSuffix ? 'pr-10' : ''} ${
              error
                ? 'border-error focus:ring-error text-error'
                : 'border-outline-variant hover:border-outline'
            } ${className}`}
            {...props}
          />

          {iconSuffix && (
            <div className="absolute right-3 text-on-surface-variant flex items-center justify-center">
              {iconSuffix}
            </div>
          )}
        </div>

        {error ? (
          <p id={`${inputId}-error`} className="text-xs text-error font-medium">
            {error}
          </p>
        ) : helperText ? (
          <p id={`${inputId}-helper`} className="text-xs text-on-surface-variant">
            {helperText}
          </p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
