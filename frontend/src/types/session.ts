/**
 * Conversational Intelligence — Session & Memory Types
 */

export interface SessionResult {
  session_id: string;
  workspace_id: string;
  session_name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  is_active: boolean;
}

export interface SessionListResult {
  sessions: SessionResult[];
  count: number;
}

export interface UserMemoryProfile {
  workspace_id: string;
  preferred_mode: string;
  topic_familiarity: Record<string, number>;
  learning_style: string;
  struggle_topics: string[];
  session_count: number;
  last_active: string;
  profile_snippet: string;
}
