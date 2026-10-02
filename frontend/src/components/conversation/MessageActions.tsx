'use client';

import React, { useState } from 'react';
import { Copy, Check, RotateCcw, ThumbsUp, ThumbsDown } from 'lucide-react';
import { IconButton } from '../primitives';

export interface MessageActionsProps {
  content: string;
  onRegenerate?: () => void;
}

export const MessageActions: React.FC<MessageActionsProps> = ({
  content,
  onRegenerate,
}) => {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  return (
    <div className="flex items-center gap-1 mt-2 text-on-surface-variant opacity-80 hover:opacity-100 transition-opacity">
      <IconButton
        label={copied ? 'Copied to clipboard' : 'Copy response'}
        size="sm"
        onClick={handleCopy}
      >
        {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
      </IconButton>

      {onRegenerate && (
        <IconButton
          label="Regenerate response"
          size="sm"
          onClick={onRegenerate}
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </IconButton>
      )}

      <IconButton
        label="Helpful"
        size="sm"
        active={feedback === 'up'}
        onClick={() => setFeedback(feedback === 'up' ? null : 'up')}
      >
        <ThumbsUp className={`w-3.5 h-3.5 ${feedback === 'up' ? 'text-primary' : ''}`} />
      </IconButton>

      <IconButton
        label="Not helpful"
        size="sm"
        active={feedback === 'down'}
        onClick={() => setFeedback(feedback === 'down' ? null : 'down')}
      >
        <ThumbsDown className={`w-3.5 h-3.5 ${feedback === 'down' ? 'text-error' : ''}`} />
      </IconButton>
    </div>
  );
};
