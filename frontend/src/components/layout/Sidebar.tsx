'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Server, Moon, Sun, Database, Menu, X, ArrowLeft } from 'lucide-react';
import { useTheme } from 'next-themes';
import { getSystemHealth } from '@/lib/api';
import { HEALTH_STATUS_CONFIG, POLLING_INTERVALS, HealthStatus } from '@/lib/constants';
import { IconButton } from '../primitives';

const navItems = [
  { name: 'Workspaces', href: '/', icon: LayoutDashboard },
  { name: 'System Health', href: '/health', icon: Server },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<HealthStatus>('operational');

  useEffect(() => {
    setMounted(true);
  }, []);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const checkConnection = useCallback(async () => {
    try {
      const health = await getSystemHealth();
      const statusKey = (health?.status || 'offline').toLowerCase() as HealthStatus;
      setSystemStatus(HEALTH_STATUS_CONFIG[statusKey] ? statusKey : 'operational');
    } catch {
      setSystemStatus('offline');
    }
  }, []);

  // Visibility-aware and state-adaptive polling
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    let isCancelled = false;

    const executePoll = async () => {
      if (document.hidden || isCancelled) return;
      await checkConnection();
    };

    const startPolling = () => {
      if (intervalId) clearInterval(intervalId);
      if (document.hidden) return;

      const intervalMs =
        systemStatus === 'offline'
          ? POLLING_INTERVALS.HEALTH_CHECK_RETRY_MS
          : POLLING_INTERVALS.HEALTH_CHECK_MS;

      intervalId = setInterval(executePoll, intervalMs);
    };

    void executePoll();
    startPolling();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        void executePoll();
        startPolling();
      } else {
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      isCancelled = true;
      if (intervalId) clearInterval(intervalId);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [checkConnection, systemStatus]);

  const currentConfig = HEALTH_STATUS_CONFIG[systemStatus];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-surface-container-low border-r border-outline-variant p-4 justify-between">
      {/* Top Branding & Nav */}
      <div className="flex flex-col gap-6">
        {/* App Title */}
        <div className="flex items-center justify-between px-2 pt-2">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs transition-transform group-hover:scale-105">
              <Database className="w-4 h-4 text-primary" />
            </div>
            <div>
              <span className="font-bold text-sm tracking-tight text-on-surface">CATALYST</span>
              <p className="text-[10px] text-on-surface-variant leading-none mt-0.5">Context Intelligence</p>
            </div>
          </Link>

          {/* Mobile close button */}
          <div className="md:hidden">
            <IconButton label="Close menu" size="sm" onClick={() => setMobileOpen(false)}>
              <X className="w-4 h-4" />
            </IconButton>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-primary-container text-on-primary-container font-semibold shadow-xs'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Status & Theme Control */}
      <div className="flex flex-col gap-3 pt-4 border-t border-outline-variant/60">
        {/* System Health Dot */}
        <Link
          href="/health"
          className="flex items-center justify-between px-3 py-2 rounded-lg bg-surface-container text-xs text-on-surface hover:bg-surface-container-high transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${currentConfig.dotClass}`} />
            <span className="font-medium text-[11px]">{currentConfig.label}</span>
          </div>
        </Link>

        {/* Theme Switcher Button */}
        {mounted && (
          <button
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
            className="flex items-center justify-between px-3 py-2 rounded-lg text-xs text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
          >
            <span className="font-medium">Theme</span>
            <div className="flex items-center gap-1.5 text-[11px]">
              {resolvedTheme === 'dark' ? (
                <>
                  <Moon className="w-3.5 h-3.5 text-primary" />
                  <span>Dark</span>
                </>
              ) : (
                <>
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                  <span>Light</span>
                </>
              )}
            </div>
          </button>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Top Bar with Hamburger */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-14 bg-surface-container-low border-b border-outline-variant px-4 flex items-center justify-between z-40">
        <Link href="/" className="flex items-center gap-2">
          <Database className="w-5 h-5 text-primary" />
          <span className="font-bold text-sm text-on-surface">CATALYST</span>
        </Link>
        <IconButton label="Open navigation" size="sm" onClick={() => setMobileOpen(true)}>
          <Menu className="w-5 h-5" />
        </IconButton>
      </div>

      {/* Desktop Persistent Sidebar */}
      <aside className="hidden md:flex w-60 h-screen flex-shrink-0 z-30">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative w-64 h-full z-10 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
