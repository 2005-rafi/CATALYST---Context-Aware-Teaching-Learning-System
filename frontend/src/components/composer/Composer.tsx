'use client';

import React, { useState, useRef } from 'react';
import { ArrowUp, Square, Sparkles } from 'lucide-react';
import { Textarea, IconButton } from '../primitives';

export interface ComposerProps {
  onSend: (message: string, mode: string) => void;
  onStop?: () => void;
  isGenerating?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export const Composer: React.FC<ComposerProps> = ({
  onSend,
  onStop,
  isGenerating = false,
  disabled = false,
  placeholder = 'Ask a question about your workspace documents...',
}) => {
  const [input, setInput] = useState('');
  const [mode, setMode] = useState<'simple' | 'medium' | 'expert'>('medium');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isGenerating || disabled) return;

    const trimmed = input.trim();
    setInput('');
    onSend(trimmed, mode);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4 sm:p-6 bg-background/80 backdrop-blur-md border-t border-outline-variant/60">
      <div className="max-w-3xl mx-auto flex flex-col gap-2">
        {/* Composer Card Container */}
        <div className="relative flex flex-col rounded-2xl border border-outline-variant bg-surface-container-low p-3 shadow-sm transition-all focus-within:border-outline focus-within:ring-1 focus-within:ring-outline/50">
          {/* Multiline Auto-expanding Input */}
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled || isGenerating}
            placeholder={placeholder}
            maxHeight={200}
            className="px-2 py-1 text-sm sm:text-base"
          />

          {/* Bottom Toolbar */}
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-outline-variant/40">
            {/* Mode Switcher */}
            <div className="flex items-center gap-1 bg-surface-container p-0.5 rounded-lg border border-outline-variant/60">
              {(['simple', 'medium', 'expert'] as const).map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={`px-2.5 py-1 text-[11px] font-medium rounded-md capitalize transition-all select-none ${
                    mode === m
                      ? 'bg-primary-container text-on-primary-container shadow-xs font-semibold'
                      : 'text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>

            {/* Action Buttons: Stop or Send */}
            <div className="flex items-center gap-2">
              {isGenerating ? (
                <IconButton
                  label="Stop generation"
                  variant="danger"
                  size="sm"
                  onClick={onStop}
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                </IconButton>
              ) : (
                <button
                  type="button"
                  onClick={() => handleSubmit()}
                  disabled={!input.trim() || disabled}
                  aria-label="Send prompt"
                  className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center transition-all duration-150 hover:opacity-90 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed shadow-xs"
                >
                  <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Supporting Hint */}
        <p className="text-[11px] text-center text-on-surface-variant/70 select-none">
          Press <kbd className="font-mono bg-surface-container px-1 py-0.5 rounded text-[10px]">Enter</kbd> to send, <kbd className="font-mono bg-surface-container px-1 py-0.5 rounded text-[10px]">Shift+Enter</kbd> for new line. Grounded by hybrid RAG.
        </p>
      </div>
    </div>
  );
};
