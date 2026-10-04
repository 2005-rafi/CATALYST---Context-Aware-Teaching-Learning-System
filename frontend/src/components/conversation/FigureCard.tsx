'use client';

import React, { useState } from 'react';
import {
  ImageOff,
  BookOpen,
  ZoomIn,
  X,
  BarChart2,
  TrendingUp,
  Image as ImageIcon,
  Binary,
  GitFork,
  Table as TableIcon,
  Palette,
  FileText,
  Frame,
} from 'lucide-react';
import { API_BASE_URL, ENDPOINTS } from '@/config/endpoints';
import { FigureReference } from '@/types/figure';

export type FigureData = FigureReference;

interface FigureCardProps {
  figure: FigureData;
  workspaceId: string;
}

interface FigureTypeConfig {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const FIGURE_TYPE_CONFIG: Record<string, FigureTypeConfig> = {
  diagram: { label: 'Diagram', icon: BarChart2 },
  chart: { label: 'Chart', icon: TrendingUp },
  photo: { label: 'Photo', icon: ImageIcon },
  equation: { label: 'Equation', icon: Binary },
  flowchart: { label: 'Flowchart', icon: GitFork },
  table_image: { label: 'Table', icon: TableIcon },
  illustration: { label: 'Illustration', icon: Palette },
  scanned_page: { label: 'Scanned', icon: FileText },
  unknown: { label: 'Figure', icon: Frame },
  other: { label: 'Figure', icon: Frame },
};

/**
 * FigureCard — displays an extracted PDF figure with its AI-generated caption.
 * Features: lazy loading, lightbox zoom, Lucide SVG type badge (zero emojis), page reference.
 */
export const FigureCard: React.FC<FigureCardProps> = ({ figure, workspaceId }) => {
  const [imgError, setImgError] = useState(false);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  // Construct the absolute image URL via the backend figures API
  const cleanUrl = figure.url.startsWith('/api/v1')
    ? figure.url.substring('/api/v1'.length)
    : figure.url.startsWith('/api')
      ? figure.url.substring('/api'.length)
      : figure.url;

  const imageUrl = figure.url.startsWith('http')
    ? figure.url
    : cleanUrl
      ? `${API_BASE_URL}${cleanUrl.startsWith('/') ? cleanUrl : `/${cleanUrl}`}`
      : `${API_BASE_URL}${ENDPOINTS.FIGURES.DETAIL(figure.figure_id)}?workspace_id=${encodeURIComponent(workspaceId)}`;

  const typeConfig = FIGURE_TYPE_CONFIG[figure.figure_type] || FIGURE_TYPE_CONFIG.unknown;
  const TypeIcon = typeConfig.icon;

  return (
    <>
      {/* Figure Card */}
      <div
        className="group relative flex flex-col rounded-xl border border-outline-variant/60 bg-surface-container overflow-hidden
                   shadow-xs hover:shadow-md hover:border-primary/40 transition-all duration-200 cursor-pointer w-52 flex-shrink-0"
        onClick={() => !imgError && setIsLightboxOpen(true)}
        role="button"
        aria-label={`View figure: ${figure.caption || 'Figure'}`}
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && !imgError && setIsLightboxOpen(true)}
      >
        {/* Image Container */}
        <div className="relative h-36 bg-surface-container-low flex items-center justify-center overflow-hidden">
          {!imgError ? (
            <>
              {/* Loading skeleton */}
              {!isLoaded && (
                <div className="absolute inset-0 animate-pulse bg-surface-container-highest" />
              )}
              <img
                src={imageUrl}
                alt={figure.caption || 'Document figure'}
                className={`w-full h-full object-contain transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
                loading="lazy"
                onLoad={() => setIsLoaded(true)}
                onError={() => setImgError(true)}
              />
              {/* Zoom overlay on hover */}
              {isLoaded && (
                <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                  <ZoomIn className="w-6 h-6 text-white drop-shadow-md" />
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center gap-1.5 text-on-surface-variant">
              <ImageOff className="w-7 h-7 opacity-40" />
              <span className="text-xs opacity-60">Image unavailable</span>
            </div>
          )}
        </div>

        {/* Card Footer */}
        <div className="px-3 py-2.5 flex flex-col gap-1">
          {/* Type Badge + Page Reference */}
          <div className="flex items-center justify-between gap-1.5">
            <span
              data-testid="figure-type-badge"
              className="inline-flex items-center gap-1.5 text-[10px] font-semibold text-primary bg-primary/10 rounded-full px-2 py-0.5 truncate max-w-[75%]"
            >
              <TypeIcon className="w-3 h-3 flex-shrink-0 text-primary" />
              <span>{typeConfig.label}</span>
            </span>
            <div className="flex items-center gap-1 text-[10px] text-on-surface-variant flex-shrink-0">
              <BookOpen className="w-2.5 h-2.5" />
              <span>p.{figure.page_number}</span>
            </div>
          </div>

          {/* Caption */}
          {figure.caption && (
            <p className="text-[11px] text-on-surface-variant leading-tight line-clamp-2">
              {figure.caption}
            </p>
          )}

          {/* Document Source */}
          <p className="text-[10px] text-on-surface-variant/60 truncate">
            {figure.document_name}
          </p>
        </div>
      </div>

      {/* Lightbox Modal */}
      {isLightboxOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150"
          onClick={() => setIsLightboxOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Figure lightbox"
        >
          <div
            className="relative max-w-5xl w-full max-h-[90vh] bg-surface rounded-2xl overflow-hidden shadow-2xl border border-outline-variant"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Lightbox Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-surface-container-high">
              <div className="flex items-center gap-2">
                <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary bg-primary/10 rounded-full px-2.5 py-0.5">
                  <TypeIcon className="w-3.5 h-3.5" />
                  <span>{typeConfig.label}</span>
                </div>
                <span className="text-xs text-on-surface-variant">•</span>
                <span className="text-xs text-on-surface-variant">{figure.document_name}</span>
                <span className="text-xs text-on-surface-variant">•</span>
                <span className="text-xs text-on-surface-variant">Page {figure.page_number}</span>
              </div>
              <button
                onClick={() => setIsLightboxOpen(false)}
                className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
                aria-label="Close lightbox"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Full Image */}
            <div className="flex items-center justify-center bg-surface-container-low p-4 max-h-[70vh] overflow-auto">
              <img
                src={imageUrl}
                alt={figure.caption || 'Document figure'}
                className="max-w-full max-h-full object-contain rounded-lg"
              />
            </div>

            {/* Caption */}
            {figure.caption && (
              <div className="px-4 py-3 border-t border-outline-variant bg-surface-container-low">
                <p className="text-sm text-on-surface leading-relaxed">{figure.caption}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};
