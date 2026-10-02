'use client';

import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, FileText } from 'lucide-react';

export interface SourceItem {
  file_name?: string;
  source_file?: string;
  chunk_count?: number;
  score?: number;
  text?: string;
}

export interface CitationListProps {
  sources?: SourceItem[];
}

export const CitationList: React.FC<CitationListProps> = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-outline-variant/60">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs font-medium text-on-surface-variant hover:text-primary transition-colors py-1 select-none"
      >
        <BookOpen className="w-3.5 h-3.5" />
        <span>
          {sources.length} Grounded {sources.length === 1 ? 'Source' : 'Sources'}
        </span>
        {expanded ? (
          <ChevronUp className="w-3.5 h-3.5 opacity-70" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 opacity-70" />
        )}
      </button>

      {expanded && (
        <div className="mt-2.5 flex flex-wrap gap-2 animate-in fade-in duration-200">
          {sources.map((src, idx) => {
            const fileName = src.file_name || src.source_file || `Source #${idx + 1}`;
            return (
              <div
                key={idx}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-container-high border border-outline-variant text-xs text-on-surface"
              >
                <FileText className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                <span className="font-medium truncate max-w-[200px]" title={fileName}>
                  {fileName}
                </span>
                {src.score !== undefined && (
                  <span className="text-[10px] text-on-surface-variant font-mono">
                    ({(src.score * 100).toFixed(0)}% match)
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
