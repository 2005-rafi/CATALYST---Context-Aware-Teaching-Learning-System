'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseStreamingRevealOptions {
  speedMs?: number;
  batchSize?: number;
  isNewMessage?: boolean;
  onRevealTick?: () => void;
  onComplete?: () => void;
}

export interface UseStreamingRevealReturn {
  revealedText: string;
  isRevealing: boolean;
  progress: number; // 0 to 1
  skip: () => void;
}

/**
 * useStreamingReveal
 * Progressively reveals completed or streaming text word-by-word
 * to provide a smooth, natural AI typing animation without jank.
 */
export function useStreamingReveal(
  fullText: string,
  options: UseStreamingRevealOptions = {}
): UseStreamingRevealReturn {
  const {
    speedMs = 18,
    batchSize = 2,
    isNewMessage = false,
    onRevealTick,
    onComplete,
  } = options;

  const [revealedLength, setRevealedLength] = useState<number>(() => {
    // If not a newly generated message (i.e. historical chat from DB), reveal 100% immediately
    return isNewMessage ? 0 : fullText.length;
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const skipRef = useRef(false);

  // Instant skip callback
  const skip = useCallback(() => {
    skipRef.current = true;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setRevealedLength(fullText.length);
    onComplete?.();
  }, [fullText.length, onComplete]);

  useEffect(() => {
    if (!isNewMessage || skipRef.current) {
      setRevealedLength(fullText.length);
      return;
    }

    if (!fullText) {
      setRevealedLength(0);
      return;
    }

    // Split text by word boundaries (including spaces and newlines)
    const tokens = fullText.match(/\S+|\s+/g) || [];
    if (tokens.length === 0) {
      setRevealedLength(0);
      return;
    }

    // Determine adaptive batch size based on text length to keep streaming responsive
    const totalTokens = tokens.length;
    const effectiveBatchSize = totalTokens > 400 ? 6 : totalTokens > 200 ? 4 : totalTokens > 80 ? 2 : 1;

    let currentTokenIndex = 0;
    setRevealedLength(0);

    const step = () => {
      if (skipRef.current) return;

      currentTokenIndex += effectiveBatchSize;

      if (currentTokenIndex >= totalTokens) {
        setRevealedLength(fullText.length);
        onRevealTick?.();
        onComplete?.();
      } else {
        const currentSlice = tokens.slice(0, currentTokenIndex).join('');
        setRevealedLength(currentSlice.length);
        onRevealTick?.();

        // Check if current token ends with major punctuation for natural micro-pause
        const lastToken = tokens[currentTokenIndex - 1] || '';
        const isPunctuation = /[.!?\n]$/.test(lastToken.trim());
        const nextDelay = isPunctuation ? speedMs * 2.2 : speedMs;

        timerRef.current = setTimeout(step, nextDelay);
      }
    };

    timerRef.current = setTimeout(step, speedMs);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [fullText, isNewMessage, speedMs, batchSize, onRevealTick, onComplete]);

  const revealedText = fullText.slice(0, revealedLength);
  const isRevealing = isNewMessage && revealedLength < fullText.length;
  const progress = fullText.length > 0 ? revealedLength / fullText.length : 1;

  return {
    revealedText,
    isRevealing,
    progress,
    skip,
  };
}
