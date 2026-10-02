'use client';

import { useState, useEffect, useRef, use } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, User, Bot, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { getChatHistory, sendMessage, APIError } from '@/lib/api';

interface Message {
  id?: string;
  role: string;
  message: string;
  timestamp?: string;
  model_used?: string;
  retrieval_chunks?: number;
  processing_time_ms?: number;
  created_at?: string;
  is_error?: boolean;
}

export default function ChatPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [mode, setMode] = useState('medium');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isCancelled = false;
    const fetchHistory = async () => {
      try {
        const history = await getChatHistory(workspaceId);
        if (!isCancelled) {
          setMessages(history || []);
        }
      } catch (error: unknown) {
        const err = error instanceof Error ? error : new Error(String(error));
        console.warn(`[Network Warning] Failed to fetch chat history: ${err.message}`);
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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const queryText = input.trim();
    const userMsg: Message = { role: 'user', message: queryText, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSending(true);

    try {
      const data = await sendMessage(workspaceId, queryText, mode);
      setMessages(prev => [...prev, {
        role: 'assistant',
        message: data.response,
        model_used: data.model_used,
        retrieval_chunks: data.sources ? data.sources.length : 0,
        created_at: new Date().toISOString()
      } as Message]);
    } catch (error: unknown) {
      const errorDetail = error instanceof APIError ? error.message : (error instanceof Error ? error.message : 'Unable to complete request to intelligence engine.');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        message: `⚠️ **Error:** ${errorDetail}`,
        created_at: new Date().toISOString(),
        is_error: true,
      } as Message]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
      
      {/* Mode Selector */}
      <div className="absolute top-4 right-6 z-10 flex items-center gap-2 bg-surface-container border border-border p-1 rounded-lg shadow-sm">
        {(['simple', 'medium', 'expert'] as const).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md capitalize transition-colors ${
              mode === m 
                ? 'bg-primary-container text-on-primary-container shadow-sm' 
                : 'text-on-surface-variant hover:bg-surface-variant hover:text-on-surface'
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-on-surface-variant">
            <Sparkles className="w-12 h-12 mb-4 text-primary opacity-40" />
            <h3 className="text-xl font-medium text-foreground">Context Engine Ready</h3>
            <p className="mt-2 text-center max-w-md text-sm">
              Ask questions about the documents in this workspace. The AI retrieves grounded context through FAISS, BM25, and Cross-Encoder reranking.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-4 max-w-3xl ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : msg.is_error
                    ? 'bg-rose-500/20 text-rose-500'
                    : 'bg-surface-container text-primary border border-border'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : msg.is_error ? <AlertCircle className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className="space-y-2">
                <div
                  className={`p-4 rounded-xl text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : msg.is_error
                      ? 'bg-rose-500/10 border border-rose-500/20 text-rose-600 rounded-tl-none'
                      : 'bg-surface border border-border text-foreground rounded-tl-none shadow-sm'
                  }`}
                >
                  <ReactMarkdown>{msg.message}</ReactMarkdown>
                </div>

                {msg.role === 'assistant' && !msg.is_error && (
                  <div className="flex items-center gap-3 text-xs text-on-surface-variant px-1">
                    {msg.model_used && <span>Model: {msg.model_used}</span>}
                    {msg.retrieval_chunks !== undefined && (
                      <>
                        <span>•</span>
                        <span>{msg.retrieval_chunks} Sources Used</span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-border bg-surface-container-low">
        <form onSubmit={handleSend} className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={sending}
            className="flex-1 bg-surface border border-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || sending}
            className="bg-primary hover:opacity-90 text-primary-foreground p-3 rounded-xl disabled:opacity-50 transition-opacity flex items-center justify-center shadow-sm"
          >
            {sending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
