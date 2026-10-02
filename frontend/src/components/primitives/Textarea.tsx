'use client';

import React, { useEffect, useRef } from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  autoResize?: boolean;
  maxHeight?: number;
  error?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      autoResize = true,
      maxHeight = 220,
      error,
      className = '',
      onChange,
      value,
      ...props
    },
    forwardedRef
  ) => {
    const internalRef = useRef<HTMLTextAreaElement | null>(null);

    // Merge forwarded ref and internal ref
    const setRef = (node: HTMLTextAreaElement | null) => {
      internalRef.current = node;
      if (typeof forwardedRef === 'function') {
        forwardedRef(node);
      } else if (forwardedRef) {
        forwardedRef.current = node;
      }
    };

    const handleResize = () => {
      const textarea = internalRef.current;
      if (!textarea || !autoResize) return;
      textarea.style.height = 'auto';
      const nextHeight = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = `${nextHeight}px`;
    };

    useEffect(() => {
      handleResize();
    }, [value, autoResize, maxHeight]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      handleResize();
      if (onChange) {
        onChange(e);
      }
    };

    return (
      <textarea
        ref={setRef}
        rows={1}
        value={value}
        onChange={handleChange}
        className={`w-full bg-transparent resize-none text-on-surface text-sm placeholder:text-on-surface-variant/60 focus:outline-none transition-all duration-150 leading-relaxed scrollbar-thin ${
          error ? 'text-error' : ''
        } ${className}`}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';
