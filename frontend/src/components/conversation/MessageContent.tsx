'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CodeBlock } from './CodeBlock';
import { StreamingIndicator } from './StreamingIndicator';

export interface MessageContentProps {
  content: string;
  isStreaming?: boolean;
}

/**
 * Pre-processes LLM Markdown text to fix common stream or formatting compression issues:
 * 1. Collapsed single-line tables: converts '| |---|' and '| | row |' into multi-line GFM tables.
 * 2. Dangling pipe delimiters and line transitions.
 */
function normalizeMarkdown(text: string): string {
  if (!text) return '';
  let normalized = text;

  // Fix collapsed table row boundaries where pipes meet without newlines
  if (normalized.includes('|')) {
    // Replace inline table separator patterns '| |---|' with '|\n|---|'
    normalized = normalized.replace(/\|\s*\|\s*([:\-\|]+)\s*\|\s*\|/g, '|\n| $1 |\n|');
    // Replace remaining inline row transitions '| |' with '|\n|'
    normalized = normalized.replace(/\|\s*\|\s*/g, '|\n| ');
  }

  return normalized;
}

export const MessageContent: React.FC<MessageContentProps> = ({
  content,
  isStreaming = false,
}) => {
  const processedContent = useMemo(() => normalizeMarkdown(content), [content]);

  return (
    <div className="prose max-w-none text-on-surface leading-relaxed break-words">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const isCodeBlock = match || String(children).includes('\n');

            if (isCodeBlock) {
              const language = match ? match[1] : 'text';
              return (
                <CodeBlock
                  language={language}
                  code={String(children).replace(/\n$/, '')}
                />
              );
            }

            return (
              <code
                className="bg-surface-container-high/80 text-primary border border-outline-variant/60 rounded px-1.5 py-0.5 font-mono text-[0.85em]"
                {...props}
              >
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="my-5 overflow-x-auto rounded-xl border border-outline-variant/50 bg-surface-container/40 shadow-sm">
                <table className="w-full border-collapse text-left text-sm">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return (
              <thead className="bg-surface-container-high/90 border-b border-outline-variant/60 text-on-surface font-semibold">
                {children}
              </thead>
            );
          },
          tbody({ children }) {
            return (
              <tbody className="divide-y divide-outline-variant/30 text-on-surface-variant">
                {children}
              </tbody>
            );
          },
          tr({ children }) {
            return (
              <tr className="transition-colors hover:bg-surface-container-high/40 even:bg-surface-container-low/30">
                {children}
              </tr>
            );
          },
          th({ children }) {
            return (
              <th className="px-4 py-3 text-xs font-bold uppercase tracking-wider text-primary">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="px-4 py-3 align-top text-on-surface/90 leading-relaxed text-sm">
                {children}
              </td>
            );
          },
          blockquote({ children }) {
            return (
              <blockquote className="my-3 border-l-4 border-primary/80 bg-surface-container-low/60 rounded-r-lg px-4 py-2.5 italic text-on-surface-variant">
                {children}
              </blockquote>
            );
          },
          h1({ children }) {
            return (
              <h1 className="text-xl font-bold text-on-surface mt-6 mb-3 pb-2 border-b border-outline-variant/30 flex items-center gap-2">
                {children}
              </h1>
            );
          },
          h2({ children }) {
            return (
              <h2 className="text-lg font-bold text-on-surface mt-5 mb-2.5 flex items-center gap-2">
                {children}
              </h2>
            );
          },
          h3({ children }) {
            return (
              <h3 className="text-base font-semibold text-primary mt-4 mb-2 flex items-center gap-1.5">
                {children}
              </h3>
            );
          },
          h4({ children }) {
            return (
              <h4 className="text-sm font-semibold text-on-surface mt-3 mb-1.5">
                {children}
              </h4>
            );
          },
          ul({ children }) {
            return (
              <ul className="my-2.5 ml-4 list-disc space-y-1 marker:text-primary">
                {children}
              </ul>
            );
          },
          ol({ children }) {
            return (
              <ol className="my-2.5 ml-4 list-decimal space-y-1 marker:text-primary font-medium">
                {children}
              </ol>
            );
          },
          li({ children }) {
            return (
              <li className="leading-relaxed text-on-surface-variant font-normal pl-1">
                {children}
              </li>
            );
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline underline-offset-2 font-medium transition-colors"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {processedContent}
      </ReactMarkdown>

      {isStreaming && <StreamingIndicator />}
    </div>
  );
};

