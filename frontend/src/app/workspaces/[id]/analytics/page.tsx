'use client';

import React, { useState, useEffect, use, useCallback } from 'react';
import {
  MessageSquare,
  FileText,
  Layers,
  HardDrive,
  RefreshCw,
  Clock,
  Download,
  Calendar,
  Sparkles,
  BarChart3,
  Cpu,
  Brain,
  CheckCircle2,
} from 'lucide-react';
import { getDetailedAnalytics, DetailedAnalyticsResult } from '@/lib/api';
import { Card, Button, Spinner } from '@/components/primitives';
import {
  ActivityTimelineChart,
  TopicMasteryCard,
  DocumentCorpusCard,
  InferenceEngineCard,
} from '@/components/analytics';

export default function AnalyticsPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [analytics, setAnalytics] = useState<DetailedAnalyticsResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeframeDays, setTimeframeDays] = useState<number>(14);

  const fetchStats = useCallback(
    async (isManualRefresh = false) => {
      if (isManualRefresh) setRefreshing(true);
      else setLoading(true);

      try {
        const data = await getDetailedAnalytics(workspaceId, timeframeDays);
        setAnalytics(data);
      } catch (err: unknown) {
        console.warn('Failed to load detailed analytics:', err);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [workspaceId, timeframeDays]
  );

  useEffect(() => {
    void fetchStats();
  }, [fetchStats]);

  // Export Analytics Report as Markdown file
  const handleExportReport = () => {
    if (!analytics) return;

    const reportContent = `# CATALYST Workspace Analytics Report
Workspace: ${analytics.workspace_name} (${analytics.workspace_id})
Generated: ${new Date().toLocaleString()}

## 1. Executive Summary & KPIs
- Total Conversational Queries: ${analytics.total_queries}
- Indexed Documents: ${analytics.total_documents}
- Vectorized Chunks: ${analytics.total_chunks}
- Disk & Vector Footprint: ${analytics.storage_used_mb.toFixed(2)} MB
- Cloud Groq Inferences: ${analytics.groq_requests}
- Local Private Inferences: ${analytics.local_model_requests}
- Total Active Sessions: ${analytics.total_sessions}
- Average Retrieval Depth: ${analytics.avg_chunks_per_query} chunks/query

## 2. Cognitive Memory & Topic Mastery
- Learning Style: ${analytics.learning_style}
- Preferred Depth Mode: ${analytics.preferred_mode}
- Mastered Topics Count: ${analytics.topic_mastery.filter((t) => t.level === 'Mastered').length}
- Topics Tracked:
${analytics.topic_mastery.map((t) => `  - ${t.topic}: ${t.familiarity_percent}% (${t.level}, ${t.query_count} queries)`).join('\n')}

## 3. Document Corpus & Visual RAG
${analytics.documents.map((d) => `  - ${d.file_name} (${d.file_type.toUpperCase()}): ${d.file_size_mb.toFixed(2)} MB, ${d.total_chunks} chunks, ${d.figures_count} figures`).join('\n')}
- Total Visual Figures: ${analytics.figures_summary.total_figures}

## 4. Time-Series Activity (Last ${timeframeDays} Days)
${analytics.activity_timeline.map((p) => `  - ${p.date} (${p.label}): ${p.query_count} queries, ${p.message_count} messages`).join('\n')}
`;

    const blob = new Blob([reportContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${analytics.workspace_name.toLowerCase().replace(/\s+/g, '_')}_analytics_report.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const kpis = [
    {
      title: 'Queries Executed',
      value: analytics?.total_queries ?? 0,
      subValue: `${analytics?.total_messages ?? 0} total messages`,
      description: 'Conversational queries processed',
      icon: MessageSquare,
      color: 'text-primary',
      bgColor: 'bg-primary-container text-on-primary-container',
    },
    {
      title: 'Documents Stored',
      value: analytics?.total_documents ?? 0,
      subValue: `${analytics?.documents.filter((d) => d.processing_status === 'completed').length ?? 0} indexed`,
      description: 'Active knowledge base files',
      icon: FileText,
      color: 'text-secondary',
      bgColor: 'bg-secondary-container text-on-secondary-container',
    },
    {
      title: 'Vectorized Passages',
      value: analytics?.total_chunks ?? 0,
      subValue: `${analytics?.avg_chunks_per_query ?? 0} chunks/prompt`,
      description: 'Split & embedded text passages',
      icon: Layers,
      color: 'text-tertiary',
      bgColor: 'bg-tertiary-container text-on-tertiary-container',
    },
    {
      title: 'Storage Consumed',
      value: `${(analytics?.storage_used_mb ?? 0).toFixed(2)} MB`,
      subValue: `${analytics?.figures_summary.total_figures ?? 0} figures saved`,
      description: 'Disk & FAISS vector footprint',
      icon: HardDrive,
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto w-full bg-background select-none scrollbar-thin">
      {/* Full-width Responsive Canvas Container */}
      <div className="w-full px-4 sm:px-6 md:px-10 lg:px-14 xl:px-16 py-6 sm:py-8 space-y-6 sm:space-y-8">
        {/* TOP BAR: Dashboard Header, Timeframe Selector & Export */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-outline-variant/60">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs">
                <BarChart3 className="w-4 h-4 text-primary" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-on-surface tracking-tight">
                {analytics?.workspace_name || 'Workspace'} Analytics & Telemetry
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
              Comprehensive telemetry, continuous memory mastery, and RAG retrieval intelligence.
            </p>
          </div>

          {/* Action Bar */}
          <div className="flex flex-wrap items-center gap-2.5 self-start lg:self-auto">
            {/* Timeframe Filter Buttons */}
            <div className="flex items-center gap-1 p-1 rounded-xl bg-surface-container border border-outline-variant/60 shadow-xs">
              {[
                { label: '7 Days', days: 7 },
                { label: '14 Days', days: 14 },
                { label: '30 Days', days: 30 },
              ].map((tf) => (
                <button
                  key={tf.days}
                  onClick={() => setTimeframeDays(tf.days)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    timeframeDays === tf.days
                      ? 'bg-primary text-on-primary shadow-xs'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
                  }`}
                >
                  {tf.label}
                </button>
              ))}
            </div>

            {/* Export Report Button */}
            <Button
              size="sm"
              variant="outline"
              icon={<Download className="w-3.5 h-3.5" />}
              onClick={handleExportReport}
              disabled={loading || !analytics}
              className="text-xs"
            >
              Export Report
            </Button>

            {/* Refresh Button */}
            <Button
              size="sm"
              variant="secondary"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />}
              onClick={() => void fetchStats(true)}
              disabled={loading || refreshing}
              className="text-xs"
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="py-32 flex flex-col items-center justify-center gap-3">
            <Spinner size="lg" />
            <p className="text-xs sm:text-sm text-on-surface-variant font-medium">
              Aggregating comprehensive workspace analytics & cognitive telemetry...
            </p>
          </div>
        ) : !analytics ? (
          <div className="py-24 text-center text-on-surface-variant">
            <p className="text-sm font-semibold">Unable to load analytics at this time.</p>
            <Button size="sm" variant="outline" className="mt-4" onClick={() => void fetchStats()}>
              Retry
            </Button>
          </div>
        ) : (
          <div className="space-y-6 sm:space-y-8">
            {/* 1. TOP ROW: 4 Core Dynamic KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {kpis.map((kpi) => (
                <Card
                  key={kpi.title}
                  className="p-5 flex flex-col justify-between hover:border-outline transition-colors shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-on-surface-variant">{kpi.title}</span>
                    <div className={`w-9 h-9 rounded-xl ${kpi.bgColor} flex items-center justify-center shadow-xs`}>
                      <kpi.icon className={`w-4 h-4 ${kpi.color}`} />
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
                        {kpi.value}
                      </span>
                      <span className="text-[11px] font-semibold text-primary">{kpi.subValue}</span>
                    </div>
                    <p className="text-[11px] text-on-surface-variant/80 mt-1">{kpi.description}</p>
                  </div>
                </Card>
              ))}
            </div>

            {/* 2. MIDDLE ROW: Interactive Activity Timeline Chart (Full Canvas Width) */}
            <ActivityTimelineChart
              timeline={analytics.activity_timeline}
              className="w-full"
            />

            {/* 3. BOTTOM GRID: Cognitive Topic Mastery & Inference Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Cognitive Topic Mastery & Memory */}
              <TopicMasteryCard
                topics={analytics.topic_mastery}
                struggleTopics={analytics.struggle_topics}
                learningStyle={analytics.learning_style}
                preferredMode={analytics.preferred_mode}
                className="h-full"
              />

              {/* Inference Engine & Model Distribution */}
              <InferenceEngineCard
                groqRequests={analytics.groq_requests}
                localRequests={analytics.local_model_requests}
                avgChunksPerQuery={analytics.avg_chunks_per_query}
                totalSessions={analytics.total_sessions}
                storageMb={analytics.storage_used_mb}
                className="h-full"
              />
            </div>

            {/* 4. DOCUMENT CORPUS & VISUAL RAG INGESTION */}
            <DocumentCorpusCard
              documents={analytics.documents}
              figuresSummary={analytics.figures_summary}
              className="w-full"
            />

            {/* Footer Telemetry Stamp */}
            {analytics.last_updated && (
              <div className="flex items-center justify-between pt-4 border-t border-outline-variant/40 text-xs text-on-surface-variant">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-primary" />
                  <span>Telemetry last synchronized: {new Date(analytics.last_updated).toLocaleString()}</span>
                </div>
                <span className="hidden sm:inline font-mono text-[11px] opacity-75">
                  Workspace ID: {analytics.workspace_id}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
