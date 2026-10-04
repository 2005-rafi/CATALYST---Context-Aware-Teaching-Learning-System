'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { CodeBlock } from './CodeBlock';
import { StreamingIndicator } from './StreamingIndicator';
import { useStreamingReveal } from '@/lib/hooks/useStreamingReveal';

export interface MessageContentProps {
  content: string;
  isStreaming?: boolean;
  isNewMessage?: boolean;
  onRevealTick?: () => void;
  onRevealComplete?: () => void;
}

/**
 * Sanitizes stray emojis from headings and text bodies to enforce
 * the CATALYST zero-emoji professional UI standard.
 * CRITICAL: Only collapses multiple horizontal spaces/tabs.
 * NEVER collapses or replaces newlines (\n, \r)!
 */
function cleanEmojis(text: string): string {
  if (!text) return text;
  return text
    .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F1E0}-\u{1F1FF}\u{1F900}-\u{1F9FF}]/gu, '')
    .replace(/[^\S\r\n]{2,}/g, ' '); // Only collapse multiple horizontal spaces/tabs
}

/**
 * Optimized and safe Markdown normalizer:
 * 1. Preserves fenced code blocks verbatim (never alters code contents).
 * 2. Cleans stray emojis while strictly preserving all vertical whitespace and newlines.
 * 3. Ensures headers (###) stuck to the end of a sentence have a blank line before them.
 * 4. Ensures blockquotes (>) stuck to the end of a sentence have a blank line before them.
 * 5. Separates table headers stuck onto headings on the same line.
 * 6. Repairs collapsed double-pipe table rows only when a valid table delimiter is present.
 * 7. Isolates block KaTeX math ($$...$$) with blank lines.
 */
function sanitizeAndFormatMarkdown(text: string): string {
  if (!text) return text;

  // Split out fenced code blocks so their internal code/markdown is preserved unmodified
  const segments = text.split(/(```[\s\S]*?```)/g);

  const formattedSegments = segments.map((segment) => {
    if (segment.startsWith('```') && segment.endsWith('```')) {
      return segment;
    }

    let t = segment.replace(/\r\n/g, '\n');
    t = cleanEmojis(t);

    // 1. Separate Headings: Ensure double newlines before Markdown headings when attached to preceding text
    t = t.replace(/([^\n#])\s*(#{1,6}\s+[^\n]+)/g, '$1\n\n$2');

    // 2. Separate Blockquotes: Ensure double newlines before blockquotes when attached to preceding text
    t = t.replace(/([^\n>])\s*(>\s+[^\n]+)/g, '$1\n\n$2');

    // 3. Separate table header stuck to heading on the same line
    t = t.replace(/(#{1,6}\s+[^\n\|]+?)\s*(\|)/g, '$1\n\n$2');

    // 4. Double pipes in tables: Restore newlines only if a genuine table delimiter row (|---|) is present
    if (/\|[\s:\-]+\|/.test(t)) {
      t = t.replace(/\|{2,}\s*/g, '|\n| ');
    }

    // 5. KaTeX block equations isolation: '$$ ... $$'
    t = t.replace(/([^\n])\s*(\$\$[^\$]+\$\$)/g, '$1\n\n$2\n\n');

    return t;
  });

  return formattedSegments.join('');
}

export const MessageContent: React.FC<MessageContentProps> = ({
  content,
  isStreaming = false,
  isNewMessage = false,
  onRevealTick,
  onRevealComplete,
}) => {
  // Normalize and sanitize markdown
  const processedContent = useMemo(() => sanitizeAndFormatMarkdown(content), [content]);

  // Word-by-word streaming animation engine
  const { revealedText, isRevealing, skip } = useStreamingReveal(processedContent, {
    isNewMessage,
    speedMs: 16,
    onRevealTick,
    onComplete: onRevealComplete,
  });

  const displayText = isNewMessage ? revealedText : processedContent;

  return (
    <div
      className="prose max-w-none text-on-surface leading-relaxed break-words relative cursor-default overflow-hidden"
      onClick={isRevealing ? skip : undefined}
      title={isRevealing ? 'Click to show full response' : undefined}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeRaw, rehypeKatex]}
        components={{
          // 1. Code Blocks & Inline Code
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
                className="bg-surface-container-high text-primary border border-outline-variant/60 rounded px-1.5 py-0.5 font-mono text-[0.875em]"
                {...props}
              >
                {children}
              </code>
            );
          },

          // 2. Tables (GFM standard with horizontal scroll container & clean borders)
          table({ children }) {
            return (
              <div className="my-5 overflow-x-auto rounded-xl border border-outline-variant bg-surface-container-lowest/50 shadow-xs max-w-full">
                <table className="w-full border-collapse text-left text-sm min-w-[500px]">
                  {children}
                </table>
              </div>
            );
          },
          thead({ children }) {
            return (
              <thead className="sticky top-0 bg-surface-container-high border-b-2 border-outline-variant text-on-surface font-semibold z-10">
                {children}
              </thead>
            );
          },
          tbody({ children }) {
            return (
              <tbody className="divide-y divide-outline-variant/40 text-on-surface-variant">
                {children}
              </tbody>
            );
          },
          tr({ children }) {
            return (
              <tr className="transition-colors hover:bg-surface-container/60 even:bg-surface-container-low/40">
                {children}
              </tr>
            );
          },
          th({ children }) {
            return (
              <th className="px-4 py-3 text-xs font-bold uppercase tracking-wider text-primary border-b border-outline-variant whitespace-nowrap">
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td className="px-4 py-3 align-top text-on-surface leading-relaxed text-sm border-b border-outline-variant/30">
                {children}
              </td>
            );
          },

          // 3. Blockquotes & Callouts
          blockquote({ children }) {
            return (
              <blockquote className="my-3.5 border-l-4 border-primary bg-surface-container-low rounded-r-lg px-4 py-3 italic text-on-surface-variant">
                {children}
              </blockquote>
            );
          },

          // 4. Headings (H1 - H6)
          h1({ children }) {
            return (
              <h1 className="text-xl sm:text-2xl font-bold text-on-surface mt-6 mb-3 pb-2 border-b border-outline-variant/40 flex items-center gap-2">
                {children}
              </h1>
            );
          },
          h2({ children }) {
            return (
              <h2 className="text-lg sm:text-xl font-bold text-on-surface mt-5 mb-2.5 flex items-center gap-2">
                {children}
              </h2>
            );
          },
          h3({ children }) {
            return (
              <h3 className="text-base sm:text-lg font-semibold text-primary mt-4 mb-2 flex items-center gap-2">
                {children}
              </h3>
            );
          },
          h4({ children }) {
            return (
              <h4 className="text-sm sm:text-base font-semibold text-on-surface mt-3 mb-1.5">
                {children}
              </h4>
            );
          },
          h5({ children }) {
            return (
              <h5 className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-on-surface-variant mt-2.5 mb-1">
                {children}
              </h5>
            );
          },
          h6({ children }) {
            return (
              <h6 className="text-xs font-semibold text-on-surface-variant mt-2 mb-1">
                {children}
              </h6>
            );
          },

          // 5. Ordered, Unordered & Nested Lists
          ul({ children }) {
            return (
              <ul className="my-3 ml-5 list-disc space-y-1.5 marker:text-primary">
                {children}
              </ul>
            );
          },
          ol({ children }) {
            return (
              <ol className="my-3 ml-5 list-decimal space-y-1.5 marker:text-primary font-medium">
                {children}
              </ol>
            );
          },
          li({ children }) {
            return (
              <li className="leading-relaxed text-on-surface font-normal pl-1">
                {children}
              </li>
            );
          },

          // 6. Task Lists
          input({ type, checked, ...props }) {
            if (type === 'checkbox') {
              return (
                <input
                  type="checkbox"
                  checked={checked}
                  readOnly
                  className="mr-2 rounded border-outline-variant text-primary focus:ring-primary h-3.5 w-3.5 align-middle accent-primary cursor-default"
                  {...props}
                />
              );
            }
            return <input type={type} {...props} />;
          },

          // 7. Typography Emphasis
          strong({ children }) {
            return <strong className="font-semibold text-on-surface">{children}</strong>;
          },
          em({ children }) {
            return <em className="italic text-on-surface">{children}</em>;
          },
          del({ children }) {
            return <del className="line-through text-on-surface-variant/70">{children}</del>;
          },

          // 8. Paragraphs
          p({ children }) {
            return (
              <p className="my-2.5 leading-relaxed text-on-surface text-sm sm:text-base">
                {children}
              </p>
            );
          },

          // 9. Links
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

          // 10. Horizontal Rules
          hr() {
            return <hr className="my-6 border-0 border-t border-outline-variant/60" />;
          },

          // 11. Images
          img({ src, alt }) {
            return (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={src}
                alt={alt || 'Image'}
                className="rounded-xl border border-outline-variant max-w-full h-auto my-3 shadow-xs"
              />
            );
          },

          // 12. Details / Collapsible sections
          details({ children }) {
            return (
              <details className="my-3 p-3 rounded-xl border border-outline-variant bg-surface-container-low transition-all">
                {children}
              </details>
            );
          },
          summary({ children }) {
            return (
              <summary className="font-semibold text-on-surface cursor-pointer select-none text-sm hover:text-primary transition-colors">
                {children}
              </summary>
            );
          },
        }}
      >
        {displayText}
      </ReactMarkdown>

      {/* Typing cursor during progressive reveal */}
      {isRevealing && (
        <span
          className="inline-block w-2.5 h-4.5 ml-1.5 align-middle bg-primary shadow-xs animate-pulse rounded-xs opacity-90"
          aria-hidden="true"
        />
      )}

      {isStreaming && <StreamingIndicator />}
    </div>
  );
};
