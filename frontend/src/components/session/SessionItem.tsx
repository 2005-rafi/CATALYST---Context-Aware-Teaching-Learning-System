'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Trash2, Pencil, Check, X, Sparkles, AlertTriangle } from 'lucide-react';
import { SessionResult, renameSession, deleteSession } from '@/lib/api';

interface SessionItemProps {
  session: SessionResult;
  isActive: boolean;
  onSelect: (sessionId: string) => void;
  onDeleted: (sessionId: string) => void;
  onRenamed: (sessionId: string, newName: string) => void;
}

export const SessionItem: React.FC<SessionItemProps> = ({
  session,
  isActive,
  onSelect,
  onDeleted,
  onRenamed,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(session.session_name);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditName(session.session_name);
  }, [session.session_name]);

  const handleStartEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleSaveRename = async () => {
    const trimmed = editName.trim();
    if (!trimmed || trimmed === session.session_name) {
      setIsEditing(false);
      setEditName(session.session_name);
      return;
    }
    setIsLoading(true);
    try {
      await renameSession(session.session_id, trimmed);
      onRenamed(session.session_id, trimmed);
    } catch {
      setEditName(session.session_name);
    } finally {
      setIsLoading(false);
      setIsEditing(false);
    }
  };

  const handleCancelRename = () => {
    setEditName(session.session_name);
    setIsEditing(false);
  };

  const handleConfirmDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsLoading(true);
    try {
      await deleteSession(session.session_id);
      onDeleted(session.session_id);
    } catch {
      /* swallow */
    } finally {
      setIsLoading(false);
      setIsDeleting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') void handleSaveRename();
    if (e.key === 'Escape') handleCancelRename();
  };

  // Helper to format relative or short time
  const formatTime = (isoString?: string) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div
      onClick={() => !isEditing && !isDeleting && onSelect(session.session_id)}
      className={`group relative flex items-start gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 select-none
        ${isActive
          ? 'bg-primary-container/80 text-on-primary-container shadow-xs font-medium border-l-2 border-primary pl-2.5'
          : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
        }
        ${isLoading ? 'opacity-50 pointer-events-none' : ''}
      `}
    >
      {/* Icon or Active Pulse */}
      <div className="mt-0.5 flex-shrink-0">
        <MessageSquare
          className={`w-3.5 h-3.5 transition-colors ${
            isActive ? 'text-primary' : 'text-on-surface-variant/70 group-hover:text-on-surface'
          }`}
        />
      </div>

      {/* Center Content: Title + Meta */}
      <div className="flex-1 min-w-0 pr-1">
        {isEditing ? (
          <div className="flex items-center gap-1">
            <input
              ref={inputRef}
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onKeyDown={handleKeyDown}
              onClick={(e) => e.stopPropagation()}
              className="w-full bg-surface-container border border-primary rounded px-1.5 py-0.5 text-xs text-on-surface outline-none focus:ring-1 focus:ring-primary"
              maxLength={100}
            />
          </div>
        ) : isDeleting ? (
          <div className="flex flex-col gap-1 py-0.5">
            <p className="text-[11px] font-semibold text-error flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> Delete chat?
            </p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <button
                onClick={handleConfirmDelete}
                className="px-2 py-0.5 rounded text-[10px] font-semibold bg-error text-on-error hover:opacity-90"
              >
                Delete
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); setIsDeleting(false); }}
                className="px-2 py-0.5 rounded text-[10px] font-medium bg-surface-container text-on-surface-variant hover:text-on-surface"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <>
            <p
              className={`text-xs leading-snug truncate ${
                isActive ? 'text-on-primary-container font-bold' : 'text-on-surface font-medium group-hover:text-on-surface'
              }`}
              title={session.session_name}
            >
              {session.session_name || 'Untitled Conversation'}
            </p>
            <div
              className={`flex items-center gap-1.5 mt-0.5 text-[10px] ${
                isActive ? 'text-on-primary-container/85 font-medium' : 'text-on-surface-variant font-medium'
              }`}
            >
              <span>{session.message_count} {session.message_count === 1 ? 'msg' : 'msgs'}</span>
              {(session.updated_at || session.created_at) && (
                <>
                  <span>•</span>
                  <span>{formatTime(session.updated_at || session.created_at)}</span>
                </>
              )}
            </div>
          </>
        )}
      </div>

      {/* Action buttons (Rename & Delete) */}
      {isEditing ? (
        <div className="flex items-center gap-0.5 flex-shrink-0">
          <button
            onClick={(e) => { e.stopPropagation(); void handleSaveRename(); }}
            className="p-1 rounded text-primary hover:bg-primary/10 transition-colors"
            title="Save"
          >
            <Check className="w-3 h-3" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); handleCancelRename(); }}
            className="p-1 rounded text-on-surface-variant hover:bg-surface-container-highest transition-colors"
            title="Cancel"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ) : !isDeleting && (
        <div className="hidden group-hover:flex items-center gap-0.5 flex-shrink-0 transition-opacity">
          <button
            onClick={handleStartEdit}
            className="p-1 rounded-md text-on-surface-variant/70 hover:bg-surface-container-highest hover:text-on-surface transition-colors"
            title="Rename conversation"
          >
            <Pencil className="w-3 h-3" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setIsDeleting(true); }}
            className="p-1 rounded-md text-on-surface-variant/70 hover:bg-error-container hover:text-error transition-colors"
            title="Delete conversation"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  );
};
