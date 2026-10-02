'use client';

import React from 'react';
import { User, Sparkles, AlertCircle } from 'lucide-react';
import { MessageContent } from './MessageContent';
import { CitationList, SourceItem } from './CitationList';
import { MessageActions } from './MessageActions';
import { Badge } from '../primitives';

export interface MessageProps {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  modelUsed?: string;
  sources?: SourceItem[];
  timestamp?: string;
  isError?: boolean;
  isStreaming?: boolean;
  onRegenerate?: () => void;
}

export const MessageItem: React.FC<MessageProps> = ({
  role,
  content,
  modelUsed,
  sources,
  timestamp,
  isError = false,
  isStreaming = false,
  onRegenerate,
}) => {
  const isUser = role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end my-4 animate-in fade-in duration-200">
        <div className="flex items-start gap-3 max-w-2xl flex-row-reverse">
          {/* User Avatar */}
          <div className="w-7 h-7 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center flex-shrink-0 text-xs shadow-xs mt-0.5">
            <User className="w-3.5 h-3.5" />
          </div>

          {/* User Message Bubble */}
          <div className="rounded-2xl rounded-tr-xs bg-surface-container-high border border-outline-variant/60 px-4 py-3 text-sm text-on-surface shadow-xs">
            <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  // Assistant / System Message (Editorial Block)
  return (
    <div className="flex justify-start my-6 animate-in fade-in duration-200">
      <div className="flex items-start gap-3.5 w-full max-w-3xl">
        {/* Assistant Avatar */}
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs shadow-xs mt-0.5 ${
            isError
              ? 'bg-error-container text-error'
              : 'bg-primary-container text-on-primary-container'
          }`}
        >
          {isError ? (
            <AlertCircle className="w-3.5 h-3.5" />
          ) : (
            <Sparkles className="w-3.5 h-3.5" />
          )}
        </div>

        {/* Assistant Content Container */}
        <div className="flex-1 min-w-0">
          {/* Header Metadata */}
          <div className="flex items-center gap-2 mb-2 select-none">
            <span className="text-xs font-semibold text-on-surface">CATALYST</span>
            {modelUsed && (
              <Badge variant="neutral" size="sm">
                {modelUsed}
              </Badge>
            )}
            {timestamp && (
              <span className="text-[11px] text-on-surface-variant opacity-70">
                {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>

          {/* Content Block */}
          <div
            className={`rounded-xl ${
              isError
                ? 'p-4 bg-error-container/10 border border-error/20 text-error'
                : 'text-on-surface'
            }`}
          >
            <MessageContent content={content} isStreaming={isStreaming} />
            <CitationList sources={sources} />
          </div>

          {/* Actions Toolbar */}
          {!isError && !isStreaming && (
            <MessageActions content={content} onRegenerate={onRegenerate} />
          )}
        </div>
      </div>
    </div>
  );
};
