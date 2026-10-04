'use client';

import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { IconButton } from '../primitives';

export interface CodeBlockProps {
  language?: string;
  code: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language = 'text', code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code: ', err);
    }
  };

  return (
    <div className="relative my-4 rounded-xl border border-outline-variant bg-surface-container-lowest overflow-hidden shadow-sm">
      {/* Code Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-surface-container-high border-b border-outline-variant text-xs text-on-surface-variant font-mono">
        <span className="font-semibold uppercase tracking-wider">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-md hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-primary" />
              <span className="text-[11px] text-primary font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-on-surface-variant" />
              <span className="text-[11px] text-on-surface-variant font-medium">Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Content Area with Horizontal Scrolling */}
      <div className="p-4 overflow-x-auto font-mono text-xs sm:text-sm text-on-surface leading-relaxed">
        <pre className="!bg-transparent !p-0 !m-0 !border-0">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};
