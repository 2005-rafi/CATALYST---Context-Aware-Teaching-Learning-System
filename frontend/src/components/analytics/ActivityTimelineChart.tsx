'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DailyActivityPoint } from '@/lib/api';
import { Activity, TrendingUp, Calendar, Zap } from 'lucide-react';

interface ActivityTimelineChartProps {
  timeline: DailyActivityPoint[];
  className?: string;
}

export const ActivityTimelineChart: React.FC<ActivityTimelineChartProps> = ({
  timeline,
  className = '',
}) => {
  const [hoveredPoint, setHoveredPoint] = useState<DailyActivityPoint | null>(null);

  const maxQueries = useMemo(() => {
    const max = Math.max(...timeline.map((t) => Math.max(t.query_count, t.message_count)), 1);
    // Round up to nice number for grid steps
    return max <= 5 ? 5 : max <= 10 ? 10 : Math.ceil(max / 5) * 5;
  }, [timeline]);

  const totalPeriodQueries = useMemo(
    () => timeline.reduce((acc, curr) => acc + curr.query_count, 0),
    [timeline]
  );

  const totalPeriodMessages = useMemo(
    () => timeline.reduce((acc, curr) => acc + curr.message_count, 0),
    [timeline]
  );

  const peakPoint = useMemo(() => {
    return [...timeline].sort((a, b) => b.query_count - a.query_count)[0] || null;
  }, [timeline]);

  return (
    <div
      className={`rounded-2xl border border-outline-variant/60 bg-surface-container-low p-5 sm:p-6 shadow-xs flex flex-col justify-between ${className}`}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs flex-shrink-0">
            <Activity className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="text-base font-bold text-on-surface tracking-tight flex items-center gap-2">
              <span>Query & Conversational Velocity</span>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
                Live Timeline
              </span>
            </h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Daily query prompt volume and overall conversational message throughput.
            </p>
          </div>
        </div>

        {/* Aggregate Badges */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end">
            <span className="text-xs text-on-surface-variant font-medium">Total Volume</span>
            <span className="text-sm font-bold text-on-surface">
              {totalPeriodQueries} queries • {totalPeriodMessages} msgs
            </span>
          </div>
          {peakPoint && peakPoint.query_count > 0 && (
            <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-secondary/10 border border-secondary/20 text-secondary text-xs font-semibold">
              <Zap className="w-3.5 h-3.5" />
              <span>Peak: {peakPoint.query_count} ({peakPoint.label})</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Interactive SVG Chart Canvas */}
      <div className="relative pt-8 pb-2 w-full select-none">
        {/* Tooltip Float */}
        <AnimatePresence>
          {hoveredPoint && (
            <motion.div
              initial={{ opacity: 0, y: 5, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 5, scale: 0.95 }}
              className="absolute top-0 right-4 z-20 px-3 py-1.5 rounded-xl bg-surface-container-highest border border-outline shadow-md text-xs pointer-events-none flex items-center gap-3"
            >
              <div className="flex items-center gap-1 text-on-surface font-semibold">
                <Calendar className="w-3.5 h-3.5 text-primary" />
                <span>{hoveredPoint.label}</span>
              </div>
              <span className="text-primary font-bold">
                {hoveredPoint.query_count} {hoveredPoint.query_count === 1 ? 'query' : 'queries'}
              </span>
              <span className="text-on-surface-variant font-medium">
                ({hoveredPoint.message_count} total messages)
              </span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bar & Grid Container */}
        <div className="h-52 w-full flex items-end justify-between gap-1.5 sm:gap-2 relative">
          {/* Horizontal Background Grid Lines */}
          <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-30">
            <div className="border-b border-dashed border-outline-variant w-full" />
            <div className="border-b border-dashed border-outline-variant w-full" />
            <div className="border-b border-dashed border-outline-variant w-full" />
            <div className="border-b border-outline-variant w-full" />
          </div>

          {/* Timeline Bars */}
          {timeline.map((point) => {
            const heightPercent = maxQueries > 0 ? (point.query_count / maxQueries) * 100 : 0;
            const msgHeightPercent = maxQueries > 0 ? (point.message_count / maxQueries) * 100 : 0;
            const isHovered = hoveredPoint?.date === point.date;
            const isPeak = peakPoint?.date === point.date && point.query_count > 0;

            return (
              <div
                key={point.date}
                onMouseEnter={() => setHoveredPoint(point)}
                onMouseLeave={() => setHoveredPoint(null)}
                className="flex-1 h-full flex flex-col justify-end items-center group cursor-pointer relative z-10"
              >
                {/* Visual Bar Column */}
                <div className="w-full max-w-[28px] h-full flex items-end justify-center relative">
                  {/* Message Backdrop Bar */}
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${Math.max(msgHeightPercent, 3)}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className={`w-full rounded-t-lg transition-colors ${
                      isHovered
                        ? 'bg-primary-container/80'
                        : point.message_count > 0
                        ? 'bg-surface-container-high'
                        : 'bg-surface-container/30'
                    }`}
                  />

                  {/* Query Foreground Bar */}
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${Math.max(heightPercent, point.query_count > 0 ? 6 : 0)}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut', delay: 0.05 }}
                    className={`absolute bottom-0 w-full rounded-t-lg transition-all ${
                      isPeak
                        ? 'bg-primary shadow-xs'
                        : point.query_count > 0
                        ? isHovered
                          ? 'bg-primary/90'
                          : 'bg-primary/75'
                        : 'bg-transparent'
                    }`}
                  />
                </div>

                {/* Bottom Date Label */}
                <span
                  className={`text-[10px] mt-2 transition-colors truncate max-w-[40px] text-center font-medium ${
                    isHovered
                      ? 'text-primary font-bold'
                      : 'text-on-surface-variant/80 group-hover:text-on-surface'
                  }`}
                >
                  {point.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend & Summary Footer */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-3 mt-2 border-t border-outline-variant/30 text-xs text-on-surface-variant">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-xs bg-primary" />
            <span className="font-medium text-[11px]">User Queries</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-xs bg-surface-container-high border border-outline-variant" />
            <span className="font-medium text-[11px]">Total Session Messages</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-on-surface-variant/80">
          <TrendingUp className="w-3.5 h-3.5 text-primary" />
          <span>Interactive timeline • Hover over bars for exact volume details</span>
        </div>
      </div>
    </div>
  );
};
