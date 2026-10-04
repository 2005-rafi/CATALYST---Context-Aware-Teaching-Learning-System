'use client';

import React from 'react';
import { FileText, Layers, Image as ImageIcon, HardDrive, CheckCircle2 } from 'lucide-react';
import { DocumentMetricItem, FigureMetricSummary } from '@/lib/api';

interface DocumentCorpusCardProps {
  documents: DocumentMetricItem[];
  figuresSummary?: FigureMetricSummary;
  className?: string;
}

export const DocumentCorpusCard: React.FC<DocumentCorpusCardProps> = ({
  documents,
  figuresSummary,
  className = '',
}) => {
  const totalMB = documents.reduce((acc, d) => acc + d.file_size_mb, 0);
  const totalChunks = documents.reduce((acc, d) => acc + d.total_chunks, 0);
  const totalFigures = figuresSummary?.total_figures ?? documents.reduce((acc, d) => acc + d.figures_count, 0);

  return (
    <div
      className={`rounded-2xl border border-outline-variant/60 bg-surface-container-low p-5 sm:p-6 shadow-xs flex flex-col justify-between ${className}`}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-tertiary-container text-on-tertiary-container flex items-center justify-center shadow-xs flex-shrink-0">
            <FileText className="w-5 h-5 text-tertiary" />
          </div>
          <div>
            <h3 className="text-base font-bold text-on-surface tracking-tight flex items-center gap-2">
              <span>Document Corpus & Visual Ingestion</span>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-tertiary/10 text-tertiary border border-tertiary/20">
                Vectorized RAG
              </span>
            </h3>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Breakdown of active indexed documents, vectorized passages, and extracted visual diagrams.
            </p>
          </div>
        </div>

        {/* Aggregate Pill */}
        <div className="flex items-center gap-2 text-xs font-semibold text-on-surface">
          <span className="px-2.5 py-1 rounded-lg bg-surface-container border border-outline-variant">
            {documents.length} Files
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-surface-container border border-outline-variant">
            {totalChunks} Chunks
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-surface-container border border-outline-variant">
            {totalFigures} Figures
          </span>
        </div>
      </div>

      {/* Visual Figures Category Breakdown */}
      {figuresSummary && figuresSummary.total_figures > 0 && (
        <div className="my-4 p-4 rounded-xl bg-surface-container/50 border border-outline-variant/50">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-xs font-bold text-on-surface flex items-center gap-1.5">
              <ImageIcon className="w-3.5 h-3.5 text-primary" /> Visual RAG Diagrams Extracted
            </span>
            <span className="text-xs font-semibold text-primary">{totalFigures} total figures</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {Object.entries(figuresSummary.by_type || {}).map(([type, count]) => (
              <div
                key={type}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container border border-outline-variant/40 text-xs text-on-surface font-medium"
              >
                <span className="text-primary font-bold">{count}</span>
                <span className="text-on-surface-variant">{type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Table List */}
      <div className="space-y-2 max-h-72 overflow-y-auto pr-1 scrollbar-thin">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-on-surface-variant text-xs">
            No documents uploaded to this workspace yet.
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.document_id}
              className="p-3.5 rounded-xl bg-surface-container/40 hover:bg-surface-container/70 border border-outline-variant/40 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-7 h-7 rounded-lg bg-surface-container-high flex items-center justify-center flex-shrink-0 text-xs font-bold uppercase text-primary">
                  {doc.file_type || 'PDF'}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-on-surface truncate" title={doc.file_name}>
                    {doc.file_name}
                  </p>
                  <p className="text-[10px] text-on-surface-variant mt-0.5">
                    Uploaded {doc.upload_time ? new Date(doc.upload_time).toLocaleDateString() : 'recently'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end sm:self-auto flex-shrink-0 text-xs">
                <div className="flex items-center gap-1 text-on-surface-variant font-medium">
                  <Layers className="w-3.5 h-3.5 text-secondary" />
                  <span>{doc.total_chunks} chunks</span>
                </div>
                {doc.figures_count > 0 && (
                  <div className="flex items-center gap-1 text-on-surface-variant font-medium">
                    <ImageIcon className="w-3.5 h-3.5 text-primary" />
                    <span>{doc.figures_count} figs</span>
                  </div>
                )}
                <div className="flex items-center gap-1 text-on-surface font-semibold">
                  <HardDrive className="w-3.5 h-3.5 text-amber-500" />
                  <span>{doc.file_size_mb.toFixed(2)} MB</span>
                </div>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-500">
                  <CheckCircle2 className="w-3 h-3" /> Indexed
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
