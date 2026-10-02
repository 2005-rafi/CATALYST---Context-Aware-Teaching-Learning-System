'use client';

import React, { useState, useEffect, useRef, use } from 'react';
import { Sparkles, MessageSquare, AlertCircle } from 'lucide-react';
import { getChatHistory, sendMessage, APIError } from '@/lib/api';
import { Conversation, MessageItem, SourceItem } from '@/components/conversation';
import { Composer } from '@/components/composer/Composer';
import { AgentStateIndicator, AgentState } from '@/components/agent/AgentStateIndicator';
import { Spinner, Button } from '@/components/primitives';

interface Message {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  message: string;
  model_used?: string;
  sources?: SourceItem[];
  created_at?: string;
  is_error?: boolean;
}

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [agentState, setAgentState] = useState<AgentState>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Fetch chat history on mount
  useEffect(() => {
    let isCancelled = false;
    const fetchHistory = async () => {
      try {
        const history = await getChatHistory(workspaceId);
        if (!isCancelled) {
          const parsed = (history || []).map((h) => ({
            id: h.id,
            role: (h.role as 'user' | 'assistant' | 'system') || 'assistant',
            message: h.message,
            model_used: h.model_used,
            created_at: h.created_at,
          }));
          setMessages(parsed);
        }
      } catch (err: unknown) {
        console.warn('Failed to load chat history:', err);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    void fetchHistory();
    return () => {
      isCancelled = true;
    };
  }, [workspaceId]);

  const handleSend = async (query: string, mode: string) => {
    if (!query.trim()) return;

    setErrorMessage(null);
    const userMsg: Message = {
      role: 'user',
      message: query,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setAgentState('searching');

    try {
      // Simulate progressive agent phases for smooth UX feedback
      const timer = setTimeout(() => {
        setAgentState('generating');
      }, 700);

      const data = await sendMessage(workspaceId, query, mode);
      clearTimeout(timer);

      const sourcesList: SourceItem[] = (data.sources || []).map((s: any) => ({
        file_name: s.source_file || s.file_name,
        chunk_count: s.chunk_count,
        score: s.score,
      }));

      const assistantMsg: Message = {
        role: 'assistant',
        message: data.response,
        model_used: data.model_used,
        sources: sourcesList,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setAgentState('idle');
    } catch (err: unknown) {
      setAgentState('idle');
      const detail =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Unable to reach intelligence server.';

      const errorMsg: Message = {
        role: 'assistant',
        message: `An error occurred while retrieving answer:\n\n> ${detail}`,
        created_at: new Date().toISOString(),
        is_error: true,
      };

      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setAgentState('idle');
  };

  const handleRegenerate = () => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMsg) {
      void handleSend(lastUserMsg.message, 'medium');
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative overflow-hidden">
      {/* Top Subtle Agent Activity Feedback */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 pointer-events-none">
        <AgentStateIndicator state={agentState} />
      </div>

      {/* Main Conversation Feed */}
      <Conversation isStreaming={agentState === 'generating'}>
        {loading ? (
          <div className="h-64 flex flex-col items-center justify-center gap-3">
            <Spinner size="lg" />
            <p className="text-xs text-on-surface-variant">Loading workspace messages...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full min-h-[380px] flex flex-col items-center justify-center text-center p-8 select-none">
            <div className="w-12 h-12 rounded-2xl bg-primary-container text-on-primary-container flex items-center justify-center mb-4 shadow-sm">
              <Sparkles className="w-6 h-6 text-primary" />
            </div>
            <h2 className="text-base font-semibold text-on-surface">Intelligence Ready</h2>
            <p className="text-xs text-on-surface-variant max-w-sm mt-1.5 leading-relaxed">
              Ask anything about your uploaded documents. CATALYST retrieves grounded passages via hybrid vector and lexical search to formulate verified answers.
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageItem
              key={msg.id || idx}
              role={msg.role}
              content={msg.message}
              modelUsed={msg.model_used}
              sources={msg.sources}
              timestamp={msg.created_at}
              isError={msg.is_error}
              onRegenerate={idx === messages.length - 1 && msg.role === 'assistant' ? handleRegenerate : undefined}
            />
          ))
        )}
      </Conversation>

      {/* Composer Input Area */}
      <Composer
        onSend={handleSend}
        onStop={handleStop}
        isGenerating={agentState !== 'idle'}
      />
    </div>
  );
}
