'use client';

import React from 'react';
import { Loader2, Search, BrainCircuit, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export type AgentState =
  | 'idle'
  | 'searching'
  | 'reranking'
  | 'generating'
  | 'completed'
  | 'error';

export interface AgentStateIndicatorProps {
  state: AgentState;
  customMessage?: string;
  className?: string;
}

export const AgentStateIndicator: React.FC<AgentStateIndicatorProps> = ({
  state,
  customMessage,
  className = '',
}) => {
  if (state === 'idle') return null;

  const stateConfig = {
    searching: {
      icon: <Search className="w-3.5 h-3.5 animate-pulse text-secondary" />,
      text: customMessage || 'Searching hybrid FAISS & BM25 indices...',
      containerClass: 'bg-secondary-container/20 border-secondary/30 text-on-surface',
    },
    reranking: {
      icon: <BrainCircuit className="w-3.5 h-3.5 animate-pulse text-tertiary" />,
      text: customMessage || 'Reranking candidate chunks with Cross-Encoder...',
      containerClass: 'bg-tertiary-container/20 border-tertiary/30 text-on-surface',
    },
    generating: {
      icon: <Sparkles className="w-3.5 h-3.5 animate-spin text-primary" />,
      text: customMessage || 'Synthesizing contextual response...',
      containerClass: 'bg-primary-container/20 border-primary/30 text-on-surface',
    },
    completed: {
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />,
      text: customMessage || 'Generation completed.',
      containerClass: 'bg-emerald-500/10 border-emerald-500/20 text-on-surface',
    },
    error: {
      icon: <AlertCircle className="w-3.5 h-3.5 text-error" />,
      text: customMessage || 'Execution interrupted.',
      containerClass: 'bg-error-container/20 border-error/30 text-error',
    },
  }[state];

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium backdrop-blur-sm select-none transition-all duration-200 ${stateConfig.containerClass} ${className}`}
    >
      <span className="flex-shrink-0">{stateConfig.icon}</span>
      <span>{stateConfig.text}</span>
    </div>
  );
};
