'use client';

import { useState, useEffect, use } from 'react';
import { Activity, Database, Cpu, MessageSquare, HardDrive, Loader2 } from 'lucide-react';
import { getAnalytics, AnalyticsResult } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

export default function AnalyticsPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [stats, setStats] = useState<AnalyticsResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getAnalytics(workspaceId);
        setStats(data);
      } catch (error: unknown) {
        const err = error instanceof Error ? error : new Error(String(error));
        console.warn(`[Network Warning] Failed to fetch analytics: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
    void fetchStats();
  }, [workspaceId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex justify-center items-center h-full text-on-surface-variant">
        Analytics not available for this workspace.
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto h-full overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Workspace Telemetry</h1>
        <p className="text-on-surface-variant mt-1 flex items-center gap-2 text-sm">
          <Activity className="w-4 h-4 text-primary" />
          <span>Live usage & retrieval performance statistics</span>
          {stats.last_updated && (
            <>
              <span>•</span>
              <span>Updated {formatDistanceToNow(new Date(stats.last_updated))} ago</span>
            </>
          )}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="p-5 bg-surface border border-border rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="text-sm font-medium">Total Queries</span>
            <MessageSquare className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{stats.total_queries || 0}</div>
          <p className="text-xs text-on-surface-variant mt-1">Queries processed</p>
        </div>

        <div className="p-5 bg-surface border border-border rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="text-sm font-medium">Ingested Docs</span>
            <Database className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{stats.total_documents || 0}</div>
          <p className="text-xs text-on-surface-variant mt-1">{stats.total_chunks || 0} active chunks</p>
        </div>

        <div className="p-5 bg-surface border border-border rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="text-sm font-medium">Storage Used</span>
            <HardDrive className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">
            {(stats.storage_used_mb || 0).toFixed(2)} MB
          </div>
          <p className="text-xs text-on-surface-variant mt-1">Files and FAISS vectors</p>
        </div>

        <div className="p-5 bg-surface border border-border rounded-xl shadow-sm">
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="text-sm font-medium">Groq Inference</span>
            <Cpu className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-foreground">{stats.groq_requests || 0}</div>
          <p className="text-xs text-on-surface-variant mt-1">
            {stats.local_model_requests || 0} local fallbacks
          </p>
        </div>
      </div>
    </div>
  );
}
