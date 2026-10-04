'use client';

import React from 'react';
import { Cpu, Zap, ShieldCheck, Database, Layers } from 'lucide-react';

interface InferenceEngineCardProps {
  groqRequests: number;
  localRequests: number;
  avgChunksPerQuery?: number;
  totalSessions?: number;
  storageMb?: number;
  className?: string;
}

export const InferenceEngineCard: React.FC<InferenceEngineCardProps> = ({
  groqRequests,
  localRequests,
  avgChunksPerQuery = 0.0,
  totalSessions = 0,
  storageMb = 0.0,
  className = '',
}) => {
  const totalRequests = groqRequests + localRequests;
  const groqPercent = totalRequests > 0 ? Math.round((groqRequests / totalRequests) * 100) : 0;
  const localPercent = totalRequests > 0 ? Math.round((localRequests / totalRequests) * 100) : 0;

  return (
    <div
      className={`rounded-2xl border border-outline-variant/60 bg-surface-container-low p-5 sm:p-6 shadow-xs flex flex-col justify-between ${className}`}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs flex-shrink-0">
            <Cpu className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-base font-bold text-on-surface tracking-tight flex items-center gap-2">
              <span>Inference Distribution & Telemetry</span>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                Hybrid AI
              </span>
            </h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Workload routing between high-throughput Cloud LLMs and zero-cost local private models.
            </p>
          </div>
        </div>

        {/* Total Prompt Inferences */}
        <div className="text-right">
          <span className="text-xs text-on-surface-variant font-medium">Total Inferences</span>
          <p className="text-lg font-bold text-on-surface">{totalRequests} calls</p>
        </div>
      </div>

      {/* Segmented Visual Distribution Bar */}
      <div className="my-5">
        <div className="flex items-center justify-between text-xs font-semibold mb-2">
          <span className="text-primary flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" /> Cloud Groq ({groqPercent}%)
          </span>
          <span className="text-secondary flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" /> Local Ollama ({localPercent}%)
          </span>
        </div>

        <div className="w-full h-3 rounded-full bg-surface-container-high overflow-hidden flex shadow-inner">
          <div
            style={{ width: `${Math.max(groqPercent, totalRequests > 0 && groqRequests > 0 ? 5 : 0)}%` }}
            className="h-full bg-primary transition-all duration-700"
            title={`Groq: ${groqRequests} requests (${groqPercent}%)`}
          />
          <div
            style={{ width: `${Math.max(localPercent, totalRequests > 0 && localRequests > 0 ? 5 : 0)}%` }}
            className="h-full bg-secondary transition-all duration-700"
            title={`Local: ${localRequests} requests (${localPercent}%)`}
          />
        </div>
      </div>

      {/* Detailed Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        <div className="p-4 rounded-xl bg-surface-container/50 border border-outline-variant/40 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-on-surface flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-primary" /> Cloud Groq Acceleration
            </span>
            <span className="text-xs font-bold text-primary px-2 py-0.5 rounded bg-primary/10">
              {groqRequests} calls
            </span>
          </div>
          <p className="text-[11px] text-on-surface-variant mt-2 leading-relaxed">
            Ultra low-latency LLaMA-3.3 inference hosted on Groq LPU hardware for real-time speed.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-surface-container/50 border border-outline-variant/40 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-on-surface flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-secondary" /> Local Privacy Inference
            </span>
            <span className="text-xs font-bold text-secondary px-2 py-0.5 rounded bg-secondary/10">
              {localRequests} calls
            </span>
          </div>
          <p className="text-[11px] text-on-surface-variant mt-2 leading-relaxed">
            Zero-cost, 100% offline Qwen2.5 1.5B/7B inference executed directly on local hardware.
          </p>
        </div>
      </div>

      {/* Auxiliary Telemetry Metrics Footer */}
      <div className="grid grid-cols-3 gap-2 pt-4 mt-4 border-t border-outline-variant/30 text-center">
        <div className="p-2 rounded-lg bg-surface-container/30">
          <span className="text-[10px] text-on-surface-variant font-medium">Avg Chunks/Query</span>
          <p className="text-xs font-bold text-on-surface mt-0.5 flex items-center justify-center gap-1">
            <Layers className="w-3 h-3 text-tertiary" /> {avgChunksPerQuery}
          </p>
        </div>
        <div className="p-2 rounded-lg bg-surface-container/30">
          <span className="text-[10px] text-on-surface-variant font-medium">Active Threads</span>
          <p className="text-xs font-bold text-on-surface mt-0.5">{totalSessions} sessions</p>
        </div>
        <div className="p-2 rounded-lg bg-surface-container/30">
          <span className="text-[10px] text-on-surface-variant font-medium">Disk Footprint</span>
          <p className="text-xs font-bold text-on-surface mt-0.5 flex items-center justify-center gap-1">
            <Database className="w-3 h-3 text-amber-500" /> {storageMb.toFixed(2)} MB
          </p>
        </div>
      </div>
    </div>
  );
};
