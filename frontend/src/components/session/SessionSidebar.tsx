'use client';

import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import {
  ChevronLeft, ChevronRight, Plus, Brain, Search, X, MessageSquare, PanelLeftClose
} from 'lucide-react';
import {
  listSessions, createSession, activateSession,
  getUserProfile, SessionResult, UserMemoryProfile
} from '@/lib/api';
import { SessionItem } from './SessionItem';
import { Spinner, IconButton } from '@/components/primitives';

export interface SessionSidebarProps {
  workspaceId: string;
  activeSessionId: string | null;
  onSessionChange: (sessionId: string) => void;
  refreshTrigger?: number;
  isMobileDrawer?: boolean;
  onCloseDrawer?: () => void;
}

interface TemporalGroup {
  label: string;
  sessions: SessionResult[];
}

export const SessionSidebar: React.FC<SessionSidebarProps> = ({
  workspaceId,
  activeSessionId,
  onSessionChange,
  refreshTrigger,
  isMobileDrawer = false,
  onCloseDrawer,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [sessions, setSessions] = useState<SessionResult[]>([]);
  const [profile, setProfile] = useState<UserMemoryProfile | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const onSessionChangeRef = useRef(onSessionChange);
  useEffect(() => {
    onSessionChangeRef.current = onSessionChange;
  }, [onSessionChange]);

  const activeSessionIdRef = useRef(activeSessionId);
  useEffect(() => {
    activeSessionIdRef.current = activeSessionId;
  }, [activeSessionId]);

  const fetchData = useCallback(async () => {
    try {
      const [sessionsRes, profileRes] = await Promise.allSettled([
        listSessions(workspaceId),
        getUserProfile(workspaceId),
      ]);
      if (sessionsRes.status === 'fulfilled') {
        const sessionList = sessionsRes.value.sessions || [];
        setSessions(sessionList);
        if (!activeSessionIdRef.current && sessionList.length > 0) {
          const currentActive = sessionList.find((s) => s.is_active) || sessionList[0];
          onSessionChangeRef.current(currentActive.session_id);
        }
      }
      if (profileRes.status === 'fulfilled') setProfile(profileRes.value);
    } catch {
      /* graceful fallback */
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void fetchData();
  }, [fetchData, refreshTrigger]);

  // Keyboard Shortcuts: Ctrl+K / Cmd+K (search) and Ctrl+N / Cmd+N (new session)
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInputFocused = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';

      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCollapsed(false);
        setTimeout(() => searchInputRef.current?.focus(), 50);
      } else if ((e.metaKey || e.ctrlKey) && e.key === 'n' && !isInputFocused) {
        e.preventDefault();
        void handleNewSession();
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [workspaceId, sessions]);

  const handleNewSession = async () => {
    if (creating) return;
    setCreating(true);
    try {
      const newSession = await createSession(workspaceId);
      setSessions((prev) => [newSession, ...prev]);
      onSessionChange(newSession.session_id);
      if (isMobileDrawer && onCloseDrawer) {
        onCloseDrawer();
      }
    } catch {
      /* swallow */
    } finally {
      setCreating(false);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    if (sessionId !== activeSessionId) {
      try {
        await activateSession(sessionId, workspaceId);
        setSessions((prev) =>
          prev.map((s) => ({ ...s, is_active: s.session_id === sessionId }))
        );
        onSessionChange(sessionId);
      } catch {
        onSessionChange(sessionId);
      }
    }
    if (isMobileDrawer && onCloseDrawer) {
      onCloseDrawer();
    }
  };

  const handleSessionDeleted = (deletedId: string) => {
    setSessions((prev) => prev.filter((s) => s.session_id !== deletedId));
    if (deletedId === activeSessionId && sessions.length > 1) {
      const next = sessions.find((s) => s.session_id !== deletedId);
      if (next) onSessionChange(next.session_id);
    }
  };

  const handleSessionRenamed = (sessionId: string, newName: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.session_id === sessionId ? { ...s, session_name: newName } : s))
    );
  };

  // Filter sessions by search query
  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const q = searchQuery.toLowerCase();
    return sessions.filter((s) =>
      s.session_name.toLowerCase().includes(q)
    );
  }, [sessions, searchQuery]);

  // Temporal Grouping Engine (Today, Yesterday, Previous 7 Days, Older)
  const temporalGroups = useMemo<TemporalGroup[]>(() => {
    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const startOfYesterday = new Date(startOfToday.getTime() - 24 * 60 * 60 * 1000);
    const startOf7Days = new Date(startOfToday.getTime() - 7 * 24 * 60 * 60 * 1000);

    const todayList: SessionResult[] = [];
    const yesterdayList: SessionResult[] = [];
    const last7DaysList: SessionResult[] = [];
    const olderList: SessionResult[] = [];

    for (const session of filteredSessions) {
      const d = session.updated_at || session.created_at ? new Date(session.updated_at || session.created_at) : now;
      if (d >= startOfToday) {
        todayList.push(session);
      } else if (d >= startOfYesterday) {
        yesterdayList.push(session);
      } else if (d >= startOf7Days) {
        last7DaysList.push(session);
      } else {
        olderList.push(session);
      }
    }

    const groups: TemporalGroup[] = [];
    if (todayList.length > 0) groups.push({ label: 'Today', sessions: todayList });
    if (yesterdayList.length > 0) groups.push({ label: 'Yesterday', sessions: yesterdayList });
    if (last7DaysList.length > 0) groups.push({ label: 'Previous 7 Days', sessions: last7DaysList });
    if (olderList.length > 0) groups.push({ label: 'Older', sessions: olderList });

    return groups;
  }, [filteredSessions]);

  // Collapsed View (Slim Rail on Desktop only)
  if (!isMobileDrawer && isCollapsed) {
    return (
      <aside className="hidden lg:flex flex-col items-center py-4 px-2 w-14 border-r border-outline-variant bg-surface-container-low backdrop-blur-md gap-3 z-10 select-none transition-all duration-200">
        <button
          onClick={() => setIsCollapsed(false)}
          className="p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors"
          title="Expand conversations (Ctrl+K)"
          aria-label="Expand conversations"
        >
          <ChevronRight className="w-4 h-4" />
        </button>

        <button
          onClick={handleNewSession}
          disabled={creating}
          className="w-9 h-9 rounded-xl bg-primary text-on-primary flex items-center justify-center hover:opacity-90 active:scale-95 transition-all shadow-xs disabled:opacity-50"
          title="New conversation (Ctrl+N)"
          aria-label="New conversation"
        >
          {creating ? <Spinner size="sm" /> : <Plus className="w-4 h-4 stroke-[2.5]" />}
        </button>

        <div className="w-full h-px bg-outline-variant/60 my-1" />

        {/* Mini indicator icon for active session */}
        <div className="flex flex-col gap-1.5 overflow-y-auto max-h-[60vh] w-full items-center">
          {sessions.slice(0, 10).map((s) => (
            <button
              key={s.session_id}
              onClick={() => handleSelectSession(s.session_id)}
              className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs transition-all ${
                s.session_id === activeSessionId
                  ? 'bg-primary-container text-primary font-bold ring-1 ring-primary'
                  : 'text-on-surface-variant hover:bg-surface-container'
              }`}
              title={s.session_name}
              aria-label={s.session_name}
            >
              <MessageSquare className="w-4 h-4" />
            </button>
          ))}
        </div>
      </aside>
    );
  }

  const containerClasses = isMobileDrawer
    ? 'flex flex-col w-full h-full bg-surface-container-low overflow-hidden select-none'
    : 'hidden lg:flex flex-col w-64 min-w-[16rem] max-w-[16rem] border-r border-outline-variant bg-surface-container-low backdrop-blur-md overflow-hidden z-10 select-none transition-all duration-200';

  return (
    <aside className={containerClasses}>
      {/* Top Header & Collapse Control */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-outline-variant/60">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-primary" />
          <span className="text-sm font-bold text-on-surface tracking-tight">
            Conversations
          </span>
          <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-[11px] font-semibold text-on-surface-variant">
            {sessions.length}
          </span>
        </div>
        
        {isMobileDrawer ? (
          onCloseDrawer && (
            <IconButton label="Close conversations" size="sm" onClick={onCloseDrawer}>
              <X className="w-4 h-4" />
            </IconButton>
          )
        ) : (
          <button
            onClick={() => setIsCollapsed(true)}
            className="p-1.5 rounded-lg text-on-surface-variant/70 hover:bg-surface-container-high hover:text-on-surface transition-colors"
            title="Collapse sidebar"
            aria-label="Collapse sidebar"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Action CTA: New Conversation */}
      <div className="px-3.5 pt-3.5 pb-2.5 flex flex-col gap-2.5">
        <button
          onClick={handleNewSession}
          disabled={creating}
          className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold
            bg-primary text-on-primary hover:opacity-95 active:scale-[0.98]
            transition-all duration-150 shadow-xs disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <div className="flex items-center gap-2">
            {creating ? (
              <Spinner size="sm" />
            ) : (
              <Plus className="w-4 h-4 stroke-[2.5]" />
            )}
            <span>New Conversation</span>
          </div>
          <kbd className="hidden group-hover:inline-block px-1.5 py-0.5 rounded bg-surface-container-highest/60 text-[10px] font-mono text-on-primary">
            Ctrl+N
          </kbd>
        </button>

        {/* Quick Search Bar */}
        <div className="relative flex items-center">
          <Search className="absolute left-3 w-3.5 h-3.5 text-on-surface-variant/60 pointer-events-none" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-9 pr-8 py-2 bg-surface-container border border-outline-variant/60 rounded-lg text-xs text-on-surface placeholder:text-on-surface-variant/60 outline-none focus:border-primary focus:ring-1 focus:ring-primary/40 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 p-0.5 rounded text-on-surface-variant/60 hover:text-on-surface"
              aria-label="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Grouped Session List */}
      <div className="flex-1 overflow-y-auto px-2.5 pb-3 space-y-3 min-h-0">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <Spinner size="sm" />
            <p className="text-xs text-on-surface-variant/70">Loading sessions...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2 text-center px-3">
            <MessageSquare className="w-6 h-6 text-on-surface-variant/40" />
            <p className="text-xs font-medium text-on-surface-variant">
              {searchQuery ? 'No matching conversations' : 'No conversations yet'}
            </p>
            <p className="text-[11px] text-on-surface-variant/70 max-w-[12rem]">
              {searchQuery ? 'Try a different search query' : 'Click "New Conversation" above to begin.'}
            </p>
          </div>
        ) : (
          temporalGroups.map((group) => (
            <div key={group.label} className="space-y-1">
              {/* Temporal Section Header */}
              <div className="flex items-center justify-between px-2 pt-1.5 pb-0.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/70">
                  {group.label}
                </span>
                <span className="text-[10px] font-medium text-on-surface-variant/50">
                  {group.sessions.length}
                </span>
              </div>

              {/* Items in this temporal group */}
              <div className="space-y-0.5">
                {group.sessions.map((session) => (
                  <SessionItem
                    key={session.session_id}
                    session={session}
                    isActive={session.session_id === activeSessionId}
                    onSelect={handleSelectSession}
                    onDeleted={handleSessionDeleted}
                    onRenamed={handleSessionRenamed}
                  />
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* User Memory Profile Indicator (Bottom) */}
      {profile && profile.session_count > 0 && (
        <div className="px-3.5 py-3 border-t border-outline-variant/60 bg-surface-container">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-md bg-tertiary-container text-on-tertiary-container flex items-center justify-center flex-shrink-0">
              <Brain className="w-3.5 h-3.5 text-tertiary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-on-surface truncate">
                Continuous Profile Active
              </p>
              <p className="text-[10px] text-on-surface-variant truncate">
                {Object.keys(profile.topic_familiarity || {}).length} topics • {profile.session_count} chats
              </p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
