'use client';

import React, { useState, useEffect, use, useCallback } from 'react';
import { Sparkles } from 'lucide-react';
import { getChatHistory, sendMessage, APIError } from '@/services/api';
import { FigureReference, ChatSource } from '@/types';
import { Conversation, MessageItem, MessageSkeleton } from '@/components/conversation';
import { Composer } from '@/components/composer/Composer';
import { AgentStateIndicator, AgentState } from '@/components/agent/AgentStateIndicator';
import { Spinner } from '@/components/primitives';
import { useWorkspaceSession } from '@/components/providers/WorkspaceSessionProvider';

interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  message: string;
  model_used?: string;
  sources?: ChatSource[];
  figures?: FigureReference[];
  created_at?: string;
  is_error?: boolean;
}

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const sessionContext = useWorkspaceSession();
  const activeSessionId = sessionContext?.activeSessionId ?? null;
  const refreshSessions = sessionContext?.refreshSessions ?? (async () => {});

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [agentState, setAgentState] = useState<AgentState>('idle');
  const [newestAssistantId, setNewestAssistantId] = useState<string | null>(null);

  // Fetch chat history for the active session
  const fetchHistory = useCallback(async (sessionId?: string | null) => {
    setLoading(true);
    setNewestAssistantId(null);
    try {
      const history = await getChatHistory(workspaceId, sessionId || undefined);
      const parsed: Message[] = (history || []).map((h) => ({
        id: h.message_id || h.id,
        role: (h.role as 'user' | 'assistant' | 'system') || 'assistant',
        message: h.message,
        model_used: h.model_used,
        created_at: h.created_at,
        sources: h.sources,
        figures: h.figures || [],
      }));
      setMessages(parsed);
    } catch (err: unknown) {
      console.warn('Failed to load chat history:', err);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  // Load history whenever active session changes
  useEffect(() => {
    void fetchHistory(activeSessionId);
  }, [activeSessionId, fetchHistory]);

  const handleSendMessage = async (text: string, mode: string = 'medium') => {
    if (!text.trim()) return;

    const tempId = `temp-${Date.now()}`;
    const userMsg: Message = {
      id: tempId,
      role: 'user',
      message: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setAgentState('searching');

    try {
      // Step: Ingesting/Retrieving context
      setTimeout(() => {
        setAgentState((curr) => (curr === 'searching' ? 'generating' : curr));
      }, 400);

      const res = await sendMessage(workspaceId, text, mode, activeSessionId || undefined);

      const assistantMsgId = res.message_id || `resp-${Date.now()}`;
      const assistantMsg: Message = {
        id: assistantMsgId,
        role: 'assistant',
        message: res.response,
        model_used: res.model_used,
        sources: res.sources,
        figures: res.figures || [],
        created_at: new Date().toISOString(),
      };

      setNewestAssistantId(assistantMsgId);
      setMessages((prev) => [...prev, assistantMsg]);

      // If this query generated or modified a session, refresh sidebar list
      if (res.session_id && res.session_id !== activeSessionId) {
        sessionContext?.selectSession(res.session_id);
      }
      await refreshSessions();
    } catch (err: unknown) {
      let errMsg = 'Failed to generate response. Please check backend connectivity.';
      if (err instanceof APIError) {
        errMsg = err.message;
      } else if (err instanceof Error) {
        errMsg = err.message;
      }

      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        message: errMsg,
        is_error: true,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setAgentState('idle');
    }
  };

  const handleStopGeneration = () => {
    setAgentState('idle');
  };

  return (
    <div className="flex-1 flex flex-col h-full min-h-0 bg-surface-container-lowest relative overflow-hidden">
      {/* 1. Main Chat Messages Feed */}
      <div className="flex-1 overflow-y-auto min-h-0 relative flex flex-col">
        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <Spinner size="lg" />
            <p className="text-xs text-on-surface-variant font-medium">
              Loading grounded conversation history...
            </p>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto">
            <div className="w-12 h-12 rounded-2xl bg-primary-container text-primary flex items-center justify-center shadow-xs mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold text-on-surface tracking-tight">
              Grounded Learning Assistant
            </h2>
            <p className="text-xs text-on-surface-variant mt-1.5 leading-relaxed">
              Ask anything from your uploaded documents. CATALYST retrieves contextually grounded chunks and multimodal figures to synthesize answers.
            </p>
          </div>
        ) : (
          <Conversation>
            {messages.map((msg) => (
              <MessageItem
                key={msg.id || msg.created_at}
                id={msg.id}
                role={msg.role}
                content={msg.message}
                sources={msg.sources}
                figures={msg.figures}
                modelUsed={msg.model_used}
                timestamp={msg.created_at}
                isError={msg.is_error}
                workspaceId={workspaceId}
                isNewMessage={msg.id === newestAssistantId}
              />
            ))}
            {agentState !== 'idle' && (
              <MessageSkeleton state={agentState} />
            )}
          </Conversation>
        )}
      </div>

      {/* 2. Floating Agent State Indicator */}
      {agentState !== 'idle' && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30">
          <AgentStateIndicator state={agentState} />
        </div>
      )}

      {/* 3. Anchored Bottom Composer */}
      <div className="flex-shrink-0 w-full">
        <Composer
          onSend={handleSendMessage}
          onStop={handleStopGeneration}
          isGenerating={agentState !== 'idle'}
          disabled={agentState !== 'idle'}
          placeholder="Ask a question about your knowledge base documents..."
        />
      </div>
    </div>
  );
}
