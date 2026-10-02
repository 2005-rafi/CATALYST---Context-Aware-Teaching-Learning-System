'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Server, CheckCircle2, AlertCircle, RefreshCw, XCircle, ShieldCheck } from 'lucide-react';
import { getSystemHealth, SystemHealthResult } from '@/lib/api';
import { HEALTH_STATUS_CONFIG, HealthStatus } from '@/lib/constants';
import { Button, Card, Badge, Spinner } from '@/components/primitives';

export default function HealthPage() {
  const [health, setHealth] = useState<SystemHealthResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchHealth = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const data = await getSystemHealth();
      setHealth(data);
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      setHealth({
        status: 'offline',
        version: 'Unknown',
        subsystems: {
          connection: { status: 'error', detail: err.message },
        },
      });
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    const run = async () => {
      if (!isCancelled) await fetchHealth();
    };
    void run();
    return () => {
      isCancelled = true;
    };
  }, [fetchHealth]);

  const statusKey = (health?.status || 'offline').toLowerCase() as HealthStatus;
  const config = HEALTH_STATUS_CONFIG[statusKey] || HEALTH_STATUS_CONFIG.degraded;

  const getSubsystemIcon = (subsystemStatus: string) => {
    if (subsystemStatus === 'ok' || subsystemStatus === 'healthy') {
      return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
    }
    if (subsystemStatus === 'degraded' || subsystemStatus === 'warning') {
      return <AlertCircle className="w-4 h-4 text-amber-500" />;
    }
    return <XCircle className="w-4 h-4 text-error" />;
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 sm:p-10 max-w-5xl mx-auto w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
            System Health
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Real-time status of backend subsystems, FAISS vector indexes, and AI model inference.
          </p>
        </div>

        <Button
          size="sm"
          variant="outline"
          loading={isRefreshing}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          onClick={fetchHealth}
        >
          Refresh Status
        </Button>
      </div>

      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center gap-3">
          <Spinner size="lg" />
          <p className="text-xs text-on-surface-variant">Querying subsystem status endpoints...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Status Banner */}
          <Card
            className={`p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border ${config.badgeClass}`}
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-background/50 flex items-center justify-center shadow-xs flex-shrink-0">
                <Server className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold capitalize">{config.label}</h2>
                <p className="text-xs opacity-80 mt-0.5 leading-relaxed">{config.description}</p>
              </div>
            </div>

            <div className="flex-shrink-0">
              <Badge variant="neutral" size="md">
                API Version {health?.version || '1.0.0'}
              </Badge>
            </div>
          </Card>

          {/* Subsystems Breakdown Grid */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-3 select-none">
              Subsystems & Dependencies
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.entries(health?.subsystems || {}).map(([key, value]) => {
                const isOk = value.status === 'ok' || value.status === 'healthy';
                return (
                  <Card key={key} className="p-5 flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-semibold text-on-surface capitalize tracking-wide flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-primary" />
                        <span>{key} Subsystem</span>
                      </h4>
                      <p className="text-xs text-on-surface-variant mt-1.5 font-mono">
                        {value.detail ||
                          (isOk
                            ? 'Operational and serving requests normally.'
                            : 'Subsystem is currently unavailable.')}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Badge variant={isOk ? 'success' : 'error'} size="sm">
                        {value.status}
                      </Badge>
                      {getSubsystemIcon(value.status)}
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
