'use client';

import { useState, useEffect, useCallback } from 'react';
import { Server, CheckCircle2, AlertCircle, RefreshCw, XCircle, ShieldCheck } from 'lucide-react';
import { getSystemHealth, SystemHealthResult } from '@/lib/api';
import { HEALTH_STATUS_CONFIG, HealthStatus } from '@/lib/constants';

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
          connection: { status: 'error', detail: err.message }
        }
      });
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    const load = async () => {
      if (!isCancelled) {
        await fetchHealth();
      }
    };
    void load();
    return () => {
      isCancelled = true;
    };
  }, [fetchHealth]);

  const statusKey = (health?.status || 'offline').toLowerCase() as HealthStatus;
  const config = HEALTH_STATUS_CONFIG[statusKey] || HEALTH_STATUS_CONFIG.degraded;

  const getSubsystemIcon = (subsystemStatus: string) => {
    if (subsystemStatus === 'ok' || subsystemStatus === 'healthy') {
      return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    }
    if (subsystemStatus === 'degraded' || subsystemStatus === 'warning') {
      return <AlertCircle className="w-5 h-5 text-amber-500" />;
    }
    return <XCircle className="w-5 h-5 text-rose-500" />;
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">System Health</h1>
          <p className="text-on-surface-variant mt-1">Real-time status of backend subsystems and AI models.</p>
        </div>
        <button
          onClick={fetchHealth}
          disabled={isRefreshing || loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border bg-surface-container hover:bg-surface-variant text-on-surface transition-colors duration-200 text-sm font-medium shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Status Banner */}
      <div className={`border rounded-xl p-6 mb-8 flex items-center justify-between transition-all duration-300 ${config.badgeClass}`}>
        <div className="flex items-center gap-4">
          <div className="p-3 bg-background/50 rounded-lg backdrop-blur-sm">
            <Server className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-bold capitalize">{config.label}</h2>
            <p className="text-sm opacity-80 mt-0.5">{config.description}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs px-2.5 py-1 rounded-full bg-background/60 font-semibold uppercase tracking-wider">
            v{health?.version || '1.0.0'}
          </span>
        </div>
      </div>

      {/* Subsystem Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(health?.subsystems || {}).map(([key, value]) => {
          const isOk = value.status === 'ok' || value.status === 'healthy';
          return (
            <div 
              key={key} 
              className="p-5 bg-surface border border-border rounded-xl flex items-start justify-between shadow-sm hover:border-primary/50 transition-all duration-200"
            >
              <div>
                <h3 className="font-semibold text-foreground capitalize tracking-wide flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-primary" />
                  {key} Subsystem
                </h3>
                <p className="text-xs text-on-surface-variant mt-1.5 font-mono">
                  {value.detail || (isOk ? 'Operational and responding normally.' : 'Service unavailable.')}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium uppercase ${isOk ? 'bg-emerald-500/10 text-emerald-600' : 'bg-rose-500/10 text-rose-600'}`}>
                  {value.status}
                </span>
                {getSubsystemIcon(value.status)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
