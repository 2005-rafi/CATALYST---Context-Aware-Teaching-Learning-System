'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
import {
  listSessions,
  createSession,
  activateSession,
  getUserProfile,
  getWorkspace,
  SessionResult,
  UserMemoryProfile,
  WorkspaceResult,
} from '@/lib/api';

export interface WorkspaceSessionContextType {
  workspaceId: string | null;
  workspace: WorkspaceResult | null;
  sessions: SessionResult[];
  activeSessionId: string | null;
  profile: UserMemoryProfile | null;
  loading: boolean;
  creatingSession: boolean;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: React.Dispatch<React.SetStateAction<boolean>>;
  toggleSidebarCollapse: () => void;
  isMobileDrawerOpen: boolean;
  setIsMobileDrawerOpen: React.Dispatch<React.SetStateAction<boolean>>;
  toggleMobileDrawer: () => void;
  selectSession: (sessionId: string) => Promise<void>;
  createNewSession: () => Promise<SessionResult | null>;
  deleteSession: (sessionId: string) => void;
  renameSession: (sessionId: string, newName: string) => void;
  refreshSessions: () => Promise<void>;
}

const WorkspaceSessionContext = createContext<WorkspaceSessionContextType | null>(null);

export function useWorkspaceSession() {
  const context = useContext(WorkspaceSessionContext);
  return context;
}

export const WorkspaceSessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();

  const workspaceId = (params?.id as string) || null;
  const [workspace, setWorkspace] = useState<WorkspaceResult | null>(null);
  const [sessions, setSessions] = useState<SessionResult[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserMemoryProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [creatingSession, setCreatingSession] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState<boolean>(false);

  // Close mobile drawer on route navigation
  useEffect(() => {
    setIsMobileDrawerOpen(false);
  }, [pathname]);

  // Fetch workspace details and session history when workspaceId changes
  const refreshSessions = useCallback(async () => {
    if (!workspaceId) {
      setWorkspace(null);
      setSessions([]);
      setActiveSessionId(null);
      setProfile(null);
      return;
    }

    setLoading(true);
    try {
      const [wsRes, sessionsRes, profileRes] = await Promise.allSettled([
        getWorkspace(workspaceId),
        listSessions(workspaceId),
        getUserProfile(workspaceId),
      ]);

      if (wsRes.status === 'fulfilled') setWorkspace(wsRes.value);
      if (profileRes.status === 'fulfilled') setProfile(profileRes.value);

      if (sessionsRes.status === 'fulfilled') {
        const sessionList = sessionsRes.value?.sessions || [];
        setSessions(sessionList);

        // Check query param or active status for initial active session
        let querySession: string | null = null;
        if (typeof window !== 'undefined') {
          querySession = new URLSearchParams(window.location.search).get('session');
        }

        if (querySession && sessionList.some((s) => s.session_id === querySession)) {
          setActiveSessionId(querySession);
        } else if (sessionList.length > 0) {
          const currentActive = sessionList.find((s) => s.is_active) || sessionList[0];
          setActiveSessionId(currentActive.session_id);
        }
      }
    } catch (err) {
      console.warn('[WorkspaceSessionProvider] Error fetching workspace session data:', err);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    void refreshSessions();
  }, [refreshSessions]);

  const toggleSidebarCollapse = useCallback(() => {
    setIsSidebarCollapsed((prev) => !prev);
  }, []);

  const toggleMobileDrawer = useCallback(() => {
    setIsMobileDrawerOpen((prev) => !prev);
  }, []);

  const selectSession = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    if (workspaceId) {
      try {
        await activateSession(sessionId, workspaceId);
        setSessions((prev) =>
          prev.map((s) => ({ ...s, is_active: s.session_id === sessionId }))
        );
      } catch (err) {
        console.warn('[WorkspaceSessionProvider] Error activating session:', err);
      }
    }
    setIsMobileDrawerOpen(false);
  }, [workspaceId]);

  const createNewSession = useCallback(async () => {
    if (!workspaceId || creatingSession) return null;
    setCreatingSession(true);
    try {
      const newSession = await createSession(workspaceId);
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.session_id);
      setIsMobileDrawerOpen(false);
      return newSession;
    } catch (err) {
      console.error('[WorkspaceSessionProvider] Error creating new session:', err);
      return null;
    } finally {
      setCreatingSession(false);
    }
  }, [workspaceId, creatingSession]);

  const deleteSession = useCallback((sessionId: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.session_id !== sessionId);
      if (sessionId === activeSessionId && updated.length > 0) {
        setActiveSessionId(updated[0].session_id);
      }
      return updated;
    });
  }, [activeSessionId]);

  const renameSession = useCallback((sessionId: string, newName: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.session_id === sessionId ? { ...s, session_name: newName } : s))
    );
  }, []);

  // Keyboard shortcut listener: Ctrl/Cmd+B to toggle sidebar collapse
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';

      if ((e.metaKey || e.ctrlKey) && e.key === 'b' && !isInput) {
        e.preventDefault();
        setIsSidebarCollapsed((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const value: WorkspaceSessionContextType = {
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
    setIsSidebarCollapsed,
    toggleSidebarCollapse,
    isMobileDrawerOpen,
    setIsMobileDrawerOpen,
    toggleMobileDrawer,
    selectSession,
    createNewSession,
    deleteSession,
    renameSession,
    refreshSessions,
  };

  return (
    <WorkspaceSessionContext.Provider value={value}>
      {children}
    </WorkspaceSessionContext.Provider>
  );
};
