'use client';

import React from 'react';
import { User, Sparkles, AlertCircle } from 'lucide-react';
import { MessageContent } from './MessageContent';
import { CitationList, SourceItem } from './CitationList';
import { MessageActions } from './MessageActions';
import { FigureCard, FigureData } from './FigureCard';
import { Badge } from '../primitives';

export interface MessageProps {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  modelUsed?: string;
  sources?: SourceItem[];
  figures?: FigureData[];
  workspaceId?: string;
  timestamp?: string;
  isError?: boolean;
  isStreaming?: boolean;
  isNewMessage?: boolean;
  onRegenerate?: () => void;
  onRevealTick?: () => void;
}

export const MessageItem: React.FC<MessageProps> = ({
  role,
  content,
  modelUsed,
  sources,
  figures,
  workspaceId,
  timestamp,
  isError = false,
  isStreaming = false,
  isNewMessage = false,
  onRegenerate,
  onRevealTick,
}) => {
  const isUser = role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end my-4 animate-in fade-in duration-200">
        <div className="flex items-start gap-3 max-w-[88%] sm:max-w-[78%] md:max-w-[68%] lg:max-w-[60%] flex-row-reverse">
          {/* User Avatar */}
          <div className="w-8 h-8 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center flex-shrink-0 text-xs shadow-xs mt-0.5">
            <User className="w-4 h-4 text-secondary" />
          </div>

          {/* User Message Bubble */}
          <div className="rounded-2xl rounded-tr-xs bg-surface-container-high border border-outline-variant/60 px-4 py-3 text-sm sm:text-base text-on-surface shadow-xs">
            <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  // Assistant / System Message (Full-Width Editorial Layout)
  return (
    <div className="flex justify-start my-6 w-full animate-in fade-in duration-200">
      <div className="flex items-start gap-3.5 sm:gap-4 w-full min-w-0">
        {/* Assistant Avatar */}
        <div
          className={`w-8 h-8 sm:w-9 sm:h-9 rounded-full flex items-center justify-center flex-shrink-0 text-xs shadow-xs mt-0.5 ${
            isError
              ? 'bg-error-container text-error'
              : 'bg-primary-container text-on-primary-container'
          }`}
        >
          {isError ? (
            <AlertCircle className="w-4 h-4" />
          ) : (
            <Sparkles className="w-4 h-4 text-primary" />
          )}
        </div>

        {/* Assistant Content Container */}
        <div className="flex-1 min-w-0">
          {/* Header Metadata */}
          <div className="flex items-center gap-2 mb-2 select-none">
            <span className="text-xs font-bold text-on-surface tracking-tight">CATALYST</span>
            {modelUsed && (
              <Badge variant="neutral" size="sm">
                {modelUsed}
              </Badge>
            )}
            {timestamp && (
              <span className="text-xs text-on-surface-variant opacity-75">
                {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>

          {/* Content Block */}
          <div
            className={`w-full rounded-xl ${
              isError
                ? 'p-4 bg-error-container/10 border border-error/20 text-error'
                : 'text-on-surface'
            }`}
          >
            <MessageContent
              content={content}
              isStreaming={isStreaming}
              isNewMessage={isNewMessage}
              onRevealTick={onRevealTick}
            />
            <CitationList sources={sources} />

            {/* Visual RAG Figures Gallery */}
            {figures && figures.length > 0 && (
              <div className="mt-4 pt-3.5 border-t border-outline-variant/40">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-on-surface-variant mb-2.5">
                  <span>Referenced Figures & Diagrams ({figures.length})</span>
                </div>
                <div className="flex gap-3 overflow-x-auto pb-2 pt-1 scrollbar-thin">
                  {figures.map((fig) => (
                    <FigureCard
                      key={fig.figure_id}
                      figure={fig}
                      workspaceId={workspaceId || ''}
                    />
                  ))}
                </div>
              </div>
            )}
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
