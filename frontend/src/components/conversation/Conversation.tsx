'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ArrowDown } from 'lucide-react';
import { Button } from '../primitives';

export interface ConversationProps {
  children: React.ReactNode;
  isStreaming?: boolean;
}

export const Conversation: React.FC<ConversationProps> = ({
  children,
  isStreaming = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const isAutoScrollEnabled = useRef(true);

  // Check scroll position relative to bottom
  const handleScroll = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);

    // If within 60px of the bottom, user is considered at the bottom
    const atBottom = distanceFromBottom < 60;
    isAutoScrollEnabled.current = atBottom;
    setShowScrollBottom(!atBottom);
  }, []);

  // Auto-scroll when new content arrives if user was already at the bottom
  useEffect(() => {
    if (isAutoScrollEnabled.current && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [children, isStreaming]);

  const scrollToBottom = () => {
    isAutoScrollEnabled.current = true;
    setShowScrollBottom(false);
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="relative flex-1 h-full overflow-hidden flex flex-col">
      {/* Scrollable Message Feed */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 md:px-10 lg:px-14 xl:px-16 py-6 space-y-4 scroll-smooth"
      >
        <div className="w-full min-w-0">
          {children}
          <div ref={bottomRef} className="h-6" />
        </div>
      </div>

      {/* Floating Jump-to-Latest Button */}
      {showScrollBottom && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <Button
            size="sm"
            variant="secondary"
            onClick={scrollToBottom}
            icon={<ArrowDown className="w-3.5 h-3.5" />}
            className="shadow-lg backdrop-blur-md border border-outline-variant bg-surface-container/95 text-xs px-3.5 py-1.5 rounded-full"
          >
            Jump to latest
          </Button>
        </div>
      )}
    </div>
  );
};
