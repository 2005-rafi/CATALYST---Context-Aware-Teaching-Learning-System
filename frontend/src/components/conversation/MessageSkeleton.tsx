'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, Search, BrainCircuit, Loader2 } from 'lucide-react';
import { AgentState } from '@/components/agent/AgentStateIndicator';

export interface MessageSkeletonProps {
  state?: AgentState;
}

export const MessageSkeleton: React.FC<MessageSkeletonProps> = ({ state = 'searching' }) => {
  const [activeStep, setActiveStep] = useState<number>(0);

  // Dynamic step progression while waiting for server response
  useEffect(() => {
    const step1 = setTimeout(() => setActiveStep(1), 1200);
    const step2 = setTimeout(() => setActiveStep(2), 2800);

    return () => {
      clearTimeout(step1);
      clearTimeout(step2);
    };
  }, []);

  const steps = [
    {
      icon: Search,
      label: 'Searching hybrid vector & BM25 indices...',
      color: 'text-secondary',
      bg: 'bg-secondary/10',
      border: 'border-secondary/30',
    },
    {
      icon: BrainCircuit,
      label: 'Evaluating evidence & reranking knowledge chunks...',
      color: 'text-tertiary',
      bg: 'bg-tertiary/10',
      border: 'border-tertiary/30',
    },
    {
      icon: Sparkles,
      label: 'Synthesizing grounded explanation & diagrams...',
      color: 'text-primary',
      bg: 'bg-primary/10',
      border: 'border-primary/30',
    },
  ];

  const currentStep = state === 'generating' ? steps[2] : steps[Math.min(activeStep, 2)];
  const StepIcon = currentStep.icon;

  return (
    <div className="flex justify-start my-6 w-full animate-in fade-in duration-300 select-none">
      <div className="flex items-start gap-3.5 sm:gap-4 w-full min-w-0">
        {/* Assistant Avatar with Glowing Shimmer Pulse */}
        <div className="relative flex-shrink-0">
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center text-xs shadow-xs mt-0.5 relative z-10">
            <Sparkles className="w-4 h-4 text-primary animate-pulse" />
          </div>
          <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping opacity-40 pointer-events-none" />
        </div>

        {/* Skeleton Content Body */}
        <div className="flex-1 min-w-0 space-y-4">
          {/* Header Metadata & Dynamic Stage Pill */}
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="text-xs font-bold text-on-surface tracking-tight">CATALYST</span>
            
            {/* Live Step Badge */}
            <div
              className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-semibold backdrop-blur-sm transition-all duration-300 ${currentStep.bg} ${currentStep.border} ${currentStep.color}`}
            >
              <StepIcon className="w-3.5 h-3.5 animate-pulse flex-shrink-0" />
              <span>{currentStep.label}</span>
              <Loader2 className="w-3 h-3 animate-spin opacity-75" />
            </div>
          </div>

          {/* Shimmering Placeholder Lines (Mimicking Heading, Text & Callout Box) */}
          <div className="w-full space-y-3 pt-1">
            {/* Heading Shimmer Bar */}
            <div className="h-5 w-52 rounded-lg bg-surface-container-high/80 relative overflow-hidden">
              <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite] bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent" />
            </div>

            {/* Paragraph Shimmer Lines */}
            <div className="space-y-2.5">
              <div className="h-3.5 w-full rounded-md bg-surface-container-high/60 relative overflow-hidden">
                <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite] bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent" />
              </div>
              <div className="h-3.5 w-[92%] rounded-md bg-surface-container-high/60 relative overflow-hidden">
                <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite] bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent" />
              </div>
              <div className="h-3.5 w-[84%] rounded-md bg-surface-container-high/60 relative overflow-hidden">
                <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite] bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent" />
              </div>
              <div className="h-3.5 w-[65%] rounded-md bg-surface-container-high/60 relative overflow-hidden">
                <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.8s_infinite] bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent" />
              </div>
            </div>

            {/* Diagram / Code Block Shimmer Box */}
            <div className="h-28 w-full rounded-xl border border-dashed border-outline-variant/60 bg-surface-container/30 relative overflow-hidden p-4 flex flex-col justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-outline-variant/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-outline-variant/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-outline-variant/80" />
                <div className="h-3 w-28 rounded bg-surface-container-high ml-2" />
              </div>
              <div className="space-y-2">
                <div className="h-2.5 w-3/4 rounded bg-surface-container-high/70" />
                <div className="h-2.5 w-1/2 rounded bg-surface-container-high/50" />
              </div>
              <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/15 dark:via-white/10 to-transparent" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
