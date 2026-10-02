'use client';

import React, { useState, useEffect, use } from 'react';
import {
  BarChart3,
  FileText,
  Layers,
  HardDrive,
  MessageSquare,
  Cpu,
  RefreshCw,
  Clock,
} from 'lucide-react';
import { getAnalytics, AnalyticsResult } from '@/lib/api';
import { Card, Button, Spinner } from '@/components/primitives';

export default function AnalyticsPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [analytics, setAnalytics] = useState<AnalyticsResult | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await getAnalytics(workspaceId);
      setAnalytics(data);
    } catch (err: unknown) {
      console.warn('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchStats();
  }, [workspaceId]);

  const metrics = [
    {
      title: 'Queries Executed',
      value: analytics?.total_queries ?? 0,
      description: 'Conversational prompts served',
      icon: MessageSquare,
      color: 'text-primary',
      bgColor: 'bg-primary-container',
    },
    {
      title: 'Documents Stored',
      value: analytics?.total_documents ?? 0,
      description: 'Active files indexed',
      icon: FileText,
      color: 'text-secondary',
      bgColor: 'bg-secondary-container',
    },
    {
      title: 'Text Chunks',
      value: analytics?.total_chunks ?? 0,
      description: 'Split & vectorized passages',
      icon: Layers,
      color: 'text-tertiary',
      bgColor: 'bg-tertiary-container',
    },
    {
      title: 'Storage Consumed',
      value: `${(analytics?.storage_used_mb ?? 0).toFixed(2)} MB`,
      description: 'Disk & FAISS vector footprint',
      icon: HardDrive,
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 sm:p-8 max-w-6xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-xl font-bold text-on-surface tracking-tight">Analytics & Index Metrics</h2>
          <p className="text-xs text-on-surface-variant mt-1">
            Real-time telemetry and resource usage statistics for this workspace.
          </p>
        </div>

        <Button
          size="sm"
          variant="outline"
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          onClick={fetchStats}
        >
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center gap-3">
          <Spinner size="lg" />
          <p className="text-xs text-on-surface-variant">Aggregating workspace analytics...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((m) => (
              <Card key={m.title} className="p-5 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-on-surface-variant">{m.title}</span>
                  <div className={`w-8 h-8 rounded-lg ${m.bgColor} flex items-center justify-center shadow-xs`}>
                    <m.icon className={`w-4 h-4 ${m.color}`} />
                  </div>
                </div>
                <div className="mt-4">
                  <span className="text-2xl font-bold tracking-tight text-on-surface">
                    {m.value}
                  </span>
                  <p className="text-[11px] text-on-surface-variant mt-1">{m.description}</p>
                </div>
              </Card>
            ))}
          </div>

          {/* Model Inference Breakdown Card */}
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-on-surface flex items-center gap-2 mb-4">
              <Cpu className="w-4 h-4 text-primary" />
              <span>Inference Distribution</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant">
                <span className="text-xs text-on-surface-variant">Cloud Groq Acceleration</span>
                <p className="text-xl font-bold text-on-surface mt-1">
                  {analytics?.groq_requests ?? 0} requests
                </p>
                <p className="text-[11px] text-on-surface-variant/80 mt-1">
                  Low-latency cloud LLM tokens
                </p>
              </div>

              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant">
                <span className="text-xs text-on-surface-variant">Local Ollama / Fallback</span>
                <p className="text-xl font-bold text-on-surface mt-1">
                  {analytics?.local_model_requests ?? 0} requests
                </p>
                <p className="text-[11px] text-on-surface-variant/80 mt-1">
                  Zero-cost local privacy inference
                </p>
              </div>
            </div>

            {analytics?.last_updated && (
              <div className="flex items-center gap-1.5 mt-6 pt-4 border-t border-outline-variant text-[11px] text-on-surface-variant">
                <Clock className="w-3.5 h-3.5" />
                <span>Last updated: {new Date(analytics.last_updated).toLocaleString()}</span>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
