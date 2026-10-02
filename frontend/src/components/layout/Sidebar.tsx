'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Server, Settings, Database, Moon, Sun, AlertTriangle } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState, useCallback } from 'react';
import { getSystemHealth } from '@/lib/api';
import { HEALTH_STATUS_CONFIG, POLLING_INTERVALS, HealthStatus } from '@/lib/constants';

const navItems = [
  { name: 'Workspaces', href: '/', icon: LayoutDashboard },
  { name: 'System Health', href: '/health', icon: Server },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [systemStatus, setSystemStatus] = useState<HealthStatus>('operational');

  // Avoid hydration mismatch
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(timer);
  }, []);

  const checkConnection = useCallback(async () => {
    try {
      const health = await getSystemHealth();
      const statusKey = (health?.status || 'offline').toLowerCase() as HealthStatus;
      setSystemStatus(HEALTH_STATUS_CONFIG[statusKey] ? statusKey : 'operational');
    } catch {
      setSystemStatus('offline');
    }
  }, []);

  // Graceful polling interval from centralized config
  useEffect(() => {
    let isCancelled = false;
    const poll = async () => {
      if (!isCancelled) {
        await checkConnection();
      }
    };
    void poll();
    const interval = setInterval(poll, POLLING_INTERVALS.HEALTH_CHECK_MS);
    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [checkConnection]);

  const currentConfig = HEALTH_STATUS_CONFIG[systemStatus];

  return (
    <aside className="w-64 bg-surface-container-low border-r border-border h-screen flex flex-col hidden md:flex transition-colors duration-300">
      <div className="p-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-primary transition-colors hover:text-on-primary-container">
          <Database className="w-6 h-6" />
          <span>CATALYST</span>
        </Link>
        <p className="text-xs text-on-surface-variant mt-1">Context Aware Teaching & Learning</p>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 ${
                isActive
                  ? 'bg-primary-container text-on-primary-container font-medium shadow-sm'
                  : 'text-on-surface-variant hover:bg-secondary-container hover:text-on-secondary-container'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Backend Disconnected Warning */}
      {systemStatus === 'offline' && (
        <div className="mx-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-md text-rose-500 flex items-start gap-2 animate-pulse">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-semibold">Backend Offline</p>
            <p className="text-[10px] opacity-80 mt-0.5">Retrying connection on port 8000...</p>
          </div>
        </div>
      )}

      <div className="p-4 border-t border-border mt-auto flex flex-col gap-2">
        {/* Dynamic Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 text-xs text-on-surface-variant">
          <span className={`w-2 h-2 rounded-full ${currentConfig.dotClass}`} />
          <span className="capitalize">{currentConfig.label}</span>
        </div>

        <button 
          className="flex items-center gap-3 px-3 py-2 w-full text-left rounded-md text-on-surface-variant hover:bg-secondary-container hover:text-on-secondary-container transition-all duration-200"
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </button>
        {mounted && (
          <button 
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
            className="flex items-center gap-3 px-3 py-2 w-full text-left rounded-md text-on-surface-variant hover:bg-secondary-container hover:text-on-secondary-container transition-all duration-200"
          >
            {resolvedTheme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            <span>{resolvedTheme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
        )}
      </div>
    </aside>
  );
}
