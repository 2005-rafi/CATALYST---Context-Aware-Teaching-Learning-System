/**
 * Chat & Conversation API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { ChatResponse, ChatHistoryItem } from '@/types/chat';

export const sendMessage = (
  workspaceId: string,
  query: string,
  mode: string = 'medium',
  sessionId?: string
) =>
  fetchWrapper<ChatResponse>(ENDPOINTS.CHAT.SEND, {
    method: 'POST',
    body: JSON.stringify({
      workspace_id: workspaceId,
      query,
      model: mode,
      session_id: sessionId || undefined,
    }),
  });

export const getChatHistory = (workspaceId: string, sessionId?: string) =>
  fetchWrapper<ChatHistoryItem[]>(ENDPOINTS.CHAT.HISTORY(workspaceId, sessionId));
