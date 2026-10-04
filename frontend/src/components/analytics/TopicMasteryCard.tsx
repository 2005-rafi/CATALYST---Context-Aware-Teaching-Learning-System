'use client';

import React, { useState, useMemo } from 'react';
import { Brain, Sparkles, AlertTriangle, CheckCircle2, Search, Award } from 'lucide-react';
import { TopicMasteryItem } from '@/lib/api';

interface TopicMasteryCardProps {
  topics: TopicMasteryItem[];
  struggleTopics?: string[];
  learningStyle?: string;
  preferredMode?: string;
  className?: string;
}

export const TopicMasteryCard: React.FC<TopicMasteryCardProps> = ({
  topics,
  struggleTopics = [],
  learningStyle = 'balanced',
  preferredMode = 'medium',
  className = '',
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredTopics = useMemo(() => {
    if (!searchTerm.trim()) return topics;
    const q = searchTerm.toLowerCase();
    return topics.filter((t) => t.topic.toLowerCase().includes(q));
  }, [topics, searchTerm]);

  const masteredCount = useMemo(() => topics.filter((t) => t.level === 'Mastered').length, [topics]);
  const proficientCount = useMemo(() => topics.filter((t) => t.level === 'Proficient').length, [topics]);
  const beginnerCount = useMemo(() => topics.filter((t) => t.level === 'Beginner').length, [topics]);

  return (
    <div
      className={`rounded-2xl border border-outline-variant/60 bg-surface-container-low p-5 sm:p-6 shadow-xs flex flex-col justify-between ${className}`}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-secondary-container text-on-secondary-container flex items-center justify-center shadow-xs flex-shrink-0">
            <Brain className="w-5 h-5 text-secondary" />
          </div>
          <div>
            <h3 className="text-base font-bold text-on-surface tracking-tight flex items-center gap-2">
              <span>Cognitive Mastery & Memory Profile</span>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-secondary/10 text-secondary border border-secondary/20">
                Continuous Profile
              </span>
            </h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Topic familiarity scores tracked dynamically across past conversational sessions.
            </p>
          </div>
        </div>

        {/* Profile Pill */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded-lg bg-surface-container border border-outline-variant font-medium text-on-surface capitalize">
            Style: {learningStyle}
          </span>
          <span className="text-xs px-2.5 py-1 rounded-lg bg-surface-container border border-outline-variant font-medium text-on-surface capitalize">
            Depth: {preferredMode}
          </span>
        </div>
      </div>

      {/* Mastery Tier Quick Stats */}
      <div className="grid grid-cols-3 gap-2.5 my-4">
        <div className="p-3 rounded-xl bg-surface-container/60 border border-outline-variant/40 flex flex-col">
          <span className="text-[11px] font-semibold text-emerald-500 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Mastered (80%+)
          </span>
          <span className="text-lg font-bold text-on-surface mt-1">{masteredCount}</span>
        </div>
        <div className="p-3 rounded-xl bg-surface-container/60 border border-outline-variant/40 flex flex-col">
          <span className="text-[11px] font-semibold text-primary flex items-center gap-1">
            <Award className="w-3 h-3" /> Proficient (50-79%)
          </span>
          <span className="text-lg font-bold text-on-surface mt-1">{proficientCount}</span>
        </div>
        <div className="p-3 rounded-xl bg-surface-container/60 border border-outline-variant/40 flex flex-col">
          <span className="text-[11px] font-semibold text-on-surface-variant flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Learning (1-49%)
          </span>
          <span className="text-lg font-bold text-on-surface mt-1">{beginnerCount}</span>
        </div>
      </div>

      {/* Struggle Topics Banner if any */}
      {struggleTopics.length > 0 && (
        <div className="mb-4 p-3 rounded-xl bg-error-container/20 border border-error/30 text-xs text-error flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Topics Needing Review: </span>
            <span>{struggleTopics.join(', ')}</span>
            <p className="text-[11px] opacity-85 mt-0.5">
              Ask follow-up questions in chat for deeper step-by-step breakdowns.
            </p>
          </div>
        </div>
      )}

      {/* Search Input */}
      {topics.length > 4 && (
        <div className="relative mb-3">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant opacity-70" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search mastery topics..."
            className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-surface-container text-xs text-on-surface font-medium placeholder:text-on-surface-variant/70 border border-outline-variant/50 focus:outline-none focus:border-primary transition-colors"
          />
        </div>
      )}

      {/* Topic Progress Bars Feed */}
      <div className="space-y-3 max-h-72 overflow-y-auto pr-1 scrollbar-thin">
        {filteredTopics.length === 0 ? (
          <div className="text-center py-8 text-on-surface-variant text-xs">
            {searchTerm ? 'No matching topics found.' : 'No topic familiarity recorded yet. Ask questions in Chat to build your memory profile!'}
          </div>
        ) : (
          filteredTopics.map((topic) => {
            const isMastered = topic.level === 'Mastered';
            const isProficient = topic.level === 'Proficient';

            return (
              <div
                key={topic.topic}
                className="p-3 rounded-xl bg-surface-container/40 hover:bg-surface-container/70 border border-outline-variant/40 transition-colors"
              >
                {/* Topic Title & Tier */}
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs font-bold text-on-surface truncate">{topic.topic}</span>
                    {topic.is_struggling && (
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-error-container text-error">
                        Review Needed
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-[11px] text-on-surface-variant font-medium">
                      {topic.query_count} {topic.query_count === 1 ? 'chat' : 'chats'}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                        isMastered
                          ? 'bg-emerald-500/15 text-emerald-500'
                          : isProficient
                          ? 'bg-primary/15 text-primary'
                          : 'bg-surface-container-high text-on-surface-variant'
                      }`}
                    >
                      {topic.familiarity_percent}% ({topic.level})
                    </span>
                  </div>
                </div>

                {/* Progress Track */}
                <div className="w-full h-2 rounded-full bg-surface-container-high overflow-hidden relative">
                  <div
                    style={{ width: `${topic.familiarity_percent}%` }}
                    className={`h-full rounded-full transition-all duration-700 ${
                      isMastered
                        ? 'bg-emerald-500'
                        : isProficient
                        ? 'bg-gradient-to-r from-secondary to-primary'
                        : 'bg-gradient-to-r from-surface-variant to-secondary'
                    }`}
                  />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
