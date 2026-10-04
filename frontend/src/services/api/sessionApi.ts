/**
 * Session API Service (Conversational Intelligence)
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { SessionResult, SessionListResult } from '@/types/session';

export const listSessions = (workspaceId: string) =>
  fetchWrapper<SessionListResult>(ENDPOINTS.SESSIONS.LIST(workspaceId));

export const createSession = (workspaceId: string, name?: string) =>
  fetchWrapper<SessionResult>(ENDPOINTS.SESSIONS.CREATE(workspaceId), {
    method: 'POST',
    body: JSON.stringify({ session_name: name ?? 'New Conversation' }),
  });

export const renameSession = (sessionId: string, name: string) =>
  fetchWrapper<SessionResult>(ENDPOINTS.SESSIONS.RENAME(sessionId), {
    method: 'PATCH',
    body: JSON.stringify({ session_name: name }),
  });

export const activateSession = (sessionId: string, workspaceId: string) =>
  fetchWrapper<SessionResult>(ENDPOINTS.SESSIONS.ACTIVATE(sessionId, workspaceId), {
    method: 'POST',
  });

export const deleteSession = (sessionId: string) =>
  fetchWrapper<null>(ENDPOINTS.SESSIONS.DELETE(sessionId), { method: 'DELETE' });
