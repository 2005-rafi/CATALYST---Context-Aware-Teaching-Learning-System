'use client';

import React, { useMemo, useRef, useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Server,
  Database,
  X,
  Plus,
  Search,
  MessageSquare,
  FileText,
  BarChart3,
  ChevronRight,
  PanelLeftClose,
  Brain,
  ArrowLeft,
  Moon,
  Sun,
  Sparkles,
} from 'lucide-react';
import { useTheme } from 'next-themes';
import { useWorkspaceSession } from '@/components/providers/WorkspaceSessionProvider';
import { SessionItem } from '@/components/session/SessionItem';
import { IconButton, Spinner, Drawer } from '@/components/primitives';
import { getSystemHealth, SessionResult } from '@/lib/api';
import { HEALTH_STATUS_CONFIG, POLLING_INTERVALS, HealthStatus } from '@/lib/constants';

interface TemporalGroup {
  label: string;
  sessions: SessionResult[];
}

export default function UnifiedSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [systemStatus, setSystemStatus] = useState<HealthStatus>('operational');
  const searchInputRef = useRef<HTMLInputElement>(null);

  const sessionContext = useWorkspaceSession();
  const {
    workspaceId,
    workspace,
    sessions,
    activeSessionId,
    profile,
    loading,
    creatingSession,
    searchQuery,
    setSearchQuery,
    isSidebarCollapsed,
    toggleSidebarCollapse,
    isMobileDrawerOpen,
    setIsMobileDrawerOpen,
    selectSession,
    createNewSession,
    deleteSession,
    renameSession,
  } = sessionContext || {
    workspaceId: null,
    workspace: null,
    sessions: [],
    activeSessionId: null,
    profile: null,
    loading: false,
    creatingSession: false,
    searchQuery: '',
    setSearchQuery: () => {},
    isSidebarCollapsed: false,
    toggleSidebarCollapse: () => {},
    isMobileDrawerOpen: false,
    setIsMobileDrawerOpen: () => {},
    selectSession: async () => {},
    createNewSession: async () => null,
    deleteSession: () => {},
    renameSession: () => {},
  };

  const isInsideWorkspace = Boolean(workspaceId);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Health check polling
  const checkConnection = useCallback(async () => {
    try {
      const health = await getSystemHealth();
      const statusKey = (health?.status || 'offline').toLowerCase() as HealthStatus;
      setSystemStatus(HEALTH_STATUS_CONFIG[statusKey] ? statusKey : 'operational');
    } catch {
      setSystemStatus('offline');
    }
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    let isCancelled = false;

    const executePoll = async () => {
      if (document.hidden || isCancelled) return;
      await checkConnection();
    };

    void executePoll();
    intervalId = setInterval(executePoll, POLLING_INTERVALS.HEALTH_CHECK_MS);

    return () => {
      isCancelled = true;
      if (intervalId) clearInterval(intervalId);
    };
  }, [checkConnection]);

  // Keyboard shortcut: Ctrl+K / Cmd+K to focus search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Filter sessions by search query
  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const q = searchQuery.toLowerCase();
    return sessions.filter((s) => s.session_name.toLowerCase().includes(q));
  }, [sessions, searchQuery]);

  // Group sessions temporally
  const temporalGroups = useMemo<TemporalGroup[]>(() => {
    if (filteredSessions.length === 0) return [];

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterday = today - 86400000;
    const sevenDaysAgo = today - 6 * 86400000;

    const groups: { [key: string]: SessionResult[] } = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      Older: [],
    };

    filteredSessions.forEach((s) => {
      const itemDate = s.updated_at ? new Date(s.updated_at).getTime() : 0;
      if (itemDate >= today) {
        groups.Today.push(s);
      } else if (itemDate >= yesterday) {
        groups.Yesterday.push(s);
      } else if (itemDate >= sevenDaysAgo) {
        groups['Previous 7 Days'].push(s);
      } else {
        groups.Older.push(s);
      }
    });

    return Object.entries(groups)
      .filter(([, list]) => list.length > 0)
      .map(([label, list]) => ({ label, sessions: list }));
  }, [filteredSessions]);

  const currentConfig = HEALTH_STATUS_CONFIG[systemStatus];

  // Mobile Workspace Navigation Tabs for Drawer
  const mobileWorkspaceTabs = useMemo(() => {
    if (!workspaceId) return [];
    return [
      {
        name: 'Chat',
        href: `/workspaces/${workspaceId}/chat`,
        icon: MessageSquare,
        active: pathname.includes('/chat'),
      },
      {
        name: 'Documents',
        href: `/workspaces/${workspaceId}/documents`,
        icon: FileText,
        active: pathname.includes('/documents'),
      },
      {
        name: 'Analytics',
        href: `/workspaces/${workspaceId}/analytics`,
        icon: BarChart3,
        active: pathname.includes('/analytics'),
      },
    ];
  }, [workspaceId, pathname]);

  // Global Navigation Tabs (Root / Health)
  const globalNavItems = [
    { name: 'All Workspaces', href: '/', icon: LayoutDashboard, active: pathname === '/' },
    { name: 'System Health', href: '/health', icon: Server, active: pathname.startsWith('/health') },
  ];

  /* -------------------------------------------------------------
   * RENDER: Collapsed Icon Rail (Desktop only, 68px width)
   * ----------------------------------------------------------- */
  const renderCollapsedRail = () => (
    <aside
      className="hidden lg:flex flex-col h-full bg-surface-container-low border-r border-outline-variant/60 w-[68px] items-center justify-between py-3 flex-shrink-0 z-30 transition-all duration-200"
      aria-label="Collapsed unified sidebar"
    >
      {/* Top Icons */}
      <div className="flex flex-col items-center gap-3.5 w-full">
        {/* App Logo */}
        <Link
          href="/"
          className="w-10 h-10 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs hover:scale-105 transition-transform"
          title="CATALYST Dashboard"
        >
          <Database className="w-5 h-5 text-primary" />
        </Link>

        {isInsideWorkspace && (
          <>
            {/* Back to Workspaces */}
            <button
              onClick={() => router.push('/')}
              className="w-9 h-9 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
              title="Back to all workspaces"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>

            {/* Quick New Chat button */}
            <button
              onClick={() => void createNewSession()}
              disabled={creatingSession}
              className="w-9 h-9 rounded-lg bg-primary text-on-primary flex items-center justify-center shadow-xs hover:bg-primary/90 transition-all"
              title="New conversation (Ctrl+N)"
            >
              {creatingSession ? <Spinner size="sm" /> : <Plus className="w-4 h-4" />}
            </button>
          </>
        )}

        {!isInsideWorkspace && (
          <div className="flex flex-col gap-2 w-full px-2 mt-2">
            {globalNavItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`w-full h-9 rounded-lg flex items-center justify-center transition-all ${
                  item.active
                    ? 'bg-primary-container text-on-primary-container font-semibold shadow-xs'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
                title={item.name}
              >
                <item.icon className="w-4 h-4" />
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Icons */}
      <div className="flex flex-col items-center gap-3 w-full px-2 pt-3 border-t border-outline-variant/60">
        {/* System Health Dot */}
        <Link
          href="/health"
          className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container transition-colors"
          title={`Status: ${currentConfig.label}`}
        >
          <span className={`w-2.5 h-2.5 rounded-full ${currentConfig.dotClass}`} />
        </Link>

        {/* Theme Toggle */}
        {mounted && (
          <button
            onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
            title={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {resolvedTheme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        )}

        {/* Expand Toggle */}
        <button
          onClick={toggleSidebarCollapse}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
          title="Expand sidebar (Ctrl+B)"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );

  /* -------------------------------------------------------------
   * RENDER: Expanded Sidebar Body Content (Desktop & Mobile Drawer)
   * ----------------------------------------------------------- */
  const renderSidebarContent = (isDrawer = false) => (
    <div className="flex flex-col h-full bg-surface-container-low border-r border-outline-variant/60 justify-between select-none overflow-hidden">
      {/* TOP: Brand Header & Context */}
      <div className="flex flex-col border-b border-outline-variant/60 bg-surface-container-low/95 backdrop-blur-md flex-shrink-0">
        {/* Brand Row */}
        <div className="flex items-center justify-between px-4 pt-3.5 pb-3">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs transition-transform group-hover:scale-105">
              <Database className="w-4 h-4 text-primary" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-on-surface">CATALYST</span>
              <span className="text-[10px] text-on-surface-variant font-medium leading-none">Context Intelligence</span>
            </div>
          </Link>

          <div className="flex items-center gap-1">
            {isDrawer ? (
              <IconButton label="Close menu" size="sm" onClick={() => setIsMobileDrawerOpen(false)}>
                <X className="w-4 h-4" />
              </IconButton>
            ) : (
              <IconButton label="Collapse sidebar" size="sm" onClick={toggleSidebarCollapse}>
                <PanelLeftClose className="w-4 h-4 text-on-surface-variant hover:text-on-surface" />
              </IconButton>
            )}
          </div>
        </div>

        {/* Mobile Drawer Only: Full Navigation Tabs */}
        {isDrawer && isInsideWorkspace && (
          <div className="px-3.5 pb-3 flex flex-col gap-2">
            <nav className="grid grid-cols-3 gap-1 p-1 bg-surface-container rounded-xl border border-outline-variant/40">
              {mobileWorkspaceTabs.map((tab) => (
                <Link
                  key={tab.name}
                  href={tab.href}
                  onClick={() => setIsMobileDrawerOpen(false)}
                  className={`flex items-center justify-center gap-1.5 py-2 px-2 rounded-lg text-xs font-bold transition-all ${
                    tab.active
                      ? 'bg-primary text-on-primary shadow-xs'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
                  }`}
                >
                  <tab.icon className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{tab.name}</span>
                </Link>
              ))}
            </nav>
          </div>
        )}

        {/* Global Nav Links when outside workspace */}
        {!isInsideWorkspace && (
          <nav className="flex flex-col gap-1 px-3.5 pb-3">
            {globalNavItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  item.active
                    ? 'bg-primary-container text-on-primary-container shadow-xs'
                    : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                }`}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        )}
      </div>

      {/* MIDDLE: Workspace Conversations Management */}
      {isInsideWorkspace ? (
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {/* Action Header: New Conversation + Search Bar */}
          <div className="p-3.5 flex flex-col gap-2.5 flex-shrink-0">
            <button
              onClick={() => void createNewSession()}
              disabled={creatingSession}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-primary text-on-primary text-xs font-bold shadow-xs hover:bg-primary/90 active:scale-[0.99] transition-all disabled:opacity-50 cursor-pointer"
            >
              <div className="flex items-center gap-2 text-on-primary">
                {creatingSession ? <Spinner size="sm" className="text-on-primary" /> : <Plus className="w-4 h-4 text-on-primary flex-shrink-0" />}
                <span className="text-on-primary font-bold">New Conversation</span>
              </div>
              <span className="text-[10px] font-mono font-semibold text-on-primary bg-on-primary/20 px-1.5 py-0.5 rounded tracking-wide">Ctrl+N</span>
            </button>

            {/* Search Input with high contrast placeholder and text */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant opacity-80" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search conversations... (Ctrl+K)"
                className="w-full pl-8 pr-7 py-2 rounded-xl bg-surface-container text-xs text-on-surface font-medium placeholder:text-on-surface-variant/80 border border-outline-variant/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/40 transition-all shadow-xs"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Session List Feed (Scrollable, Clean Vertical Rhythm) */}
          <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-4 scrollbar-thin">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-32 gap-2 text-on-surface-variant">
                <Spinner size="sm" />
                <span className="text-xs font-medium">Loading conversations...</span>
              </div>
            ) : filteredSessions.length === 0 ? (
              <div className="text-center py-10 px-4 text-on-surface-variant">
                <MessageSquare className="w-7 h-7 mx-auto mb-2 opacity-40 text-primary" />
                <p className="text-xs font-semibold text-on-surface">{searchQuery ? 'No matching conversations' : 'No conversations yet'}</p>
                <p className="text-[11px] opacity-75 mt-0.5">
                  {searchQuery ? 'Try another search term' : 'Click New Conversation to begin'}
                </p>
              </div>
            ) : (
              temporalGroups.map((group) => (
                <div key={group.label} className="space-y-1">
                  <div className="px-2 py-1 flex items-center justify-between text-[10px] font-bold tracking-wider text-on-surface-variant uppercase">
                    <span>{group.label}</span>
                    <span className="text-[10px] font-semibold opacity-70">{group.sessions.length}</span>
                  </div>
                  <div className="space-y-1">
                    {group.sessions.map((session) => (
                      <SessionItem
                        key={session.session_id}
                        session={session}
                        isActive={session.session_id === activeSessionId}
                        onSelect={(id) => void selectSession(id)}
                        onDeleted={(id) => deleteSession(id)}
                        onRenamed={(id, name) => renameSession(id, name)}
                      />
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 p-6 flex flex-col justify-center items-center text-center text-on-surface-variant">
          <Database className="w-10 h-10 opacity-30 text-primary mb-3" />
          <p className="text-xs font-bold text-on-surface">Context-Aware Intelligence</p>
          <p className="text-[11px] opacity-80 max-w-xs mt-1 leading-relaxed">
            Select a workspace to explore grounded curriculum, interactive session history, and visual diagrams.
          </p>
        </div>
      )}

      {/* FOOTER: Learning Profile & System Utility Controls */}
      <div className="flex flex-col gap-2.5 p-3.5 border-t border-outline-variant/60 bg-surface-container-low/95 backdrop-blur-md flex-shrink-0">
        {/* Continuous Memory Profile Pill */}
        {isInsideWorkspace && (
          <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-surface-container/80 border border-outline-variant/50 text-on-surface shadow-xs">
            <div className="w-7 h-7 rounded-lg bg-secondary-container text-on-secondary-container flex items-center justify-center flex-shrink-0">
              <Brain className="w-4 h-4 text-secondary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-on-surface leading-tight truncate">Continuous Profile Active</p>
              <p className="text-[10px] font-medium text-on-surface-variant truncate mt-0.5">
                {Object.keys(profile?.topic_familiarity || {}).length} topics • {profile?.session_count ?? sessions.length ?? 0} chats
              </p>
            </div>
          </div>
        )}

        {/* Health Status & Theme Switcher Bar */}
        <div className="flex items-center justify-between pt-0.5">
          {/* System Health Status */}
          <Link
            href="/health"
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg hover:bg-surface-container transition-colors text-xs text-on-surface font-medium"
          >
            <span className={`w-2.5 h-2.5 rounded-full ${currentConfig.dotClass}`} />
            <span className="text-[11px] font-semibold text-on-surface">{currentConfig.label}</span>
          </Link>

          {/* Theme Toggle Button */}
          {mounted && (
            <button
              onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-on-surface hover:bg-surface-container border border-outline-variant/40 transition-colors shadow-xs"
              title={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {resolvedTheme === 'dark' ? (
                <>
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                  <span className="text-[11px]">Light</span>
                </>
              ) : (
                <>
                  <Moon className="w-3.5 h-3.5 text-indigo-500" />
                  <span className="text-[11px]">Dark</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* 1. Desktop In-Flow Sidebar (≥ 1024px) */}
      {isSidebarCollapsed ? (
        renderCollapsedRail()
      ) : (
        <aside
          className="hidden lg:flex flex-col h-full w-[280px] flex-shrink-0 z-30 transition-all duration-200 shadow-xs"
          aria-label="Unified desktop sidebar"
        >
          {renderSidebarContent(false)}
        </aside>
      )}

      {/* 2. Mobile & Tablet Slide-Over Drawer (< 1024px) */}
      <Drawer
        isOpen={isMobileDrawerOpen}
        onClose={() => setIsMobileDrawerOpen(false)}
        side="left"
        className="w-80 max-w-[85vw] p-0"
      >
        <div className="h-full w-full">
          {renderSidebarContent(true)}
        </div>
      </Drawer>
    </>
  );
}
