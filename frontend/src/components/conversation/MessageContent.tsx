'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CodeBlock } from './CodeBlock';
import { StreamingIndicator } from './StreamingIndicator';

export interface MessageContentProps {
  content: string;
  isStreaming?: boolean;
}

export const MessageContent: React.FC<MessageContentProps> = ({
  content,
  isStreaming = false,
}) => {
  return (
    <div className="prose max-w-none text-on-surface">
      <ReactMarkdown
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
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="my-4 overflow-x-auto rounded-lg border border-outline-variant">
                <table className="min-w-full divide-y divide-outline-variant">{children}</table>
              </div>
            );
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline underline-offset-2 font-medium"
              >
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>

      {isStreaming && <StreamingIndicator />}
    </div>
  );
};
