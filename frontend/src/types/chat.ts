/**
 * Chat, Messaging & Conversation Data Models and Types
 */

import { FigureReference } from './figure';

export interface ChatSource {
  file_name: string;
  chunk_count: number;
}

export interface ChatResponse {
  response: string;
  model_used: string;
  message_id?: string;
  session_id?: string;
  sources?: ChatSource[];
  figures?: FigureReference[];
}

export interface ChatHistoryItem {
  id?: string;
  message_id?: string;
  role: 'user' | 'assistant' | 'system' | string;
  message: string;
  model_used?: string;
  created_at?: string;
  session_id?: string;
  sources?: ChatSource[];
  figures?: FigureReference[];
}
