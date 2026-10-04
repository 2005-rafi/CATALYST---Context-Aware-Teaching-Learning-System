'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { MessageSquare, FileText, BarChart3, ArrowLeft, Menu, Sparkles, Database } from 'lucide-react';
import { motion } from 'framer-motion';
import { IconButton } from '../primitives';
import { useWorkspaceSession } from '@/components/providers/WorkspaceSessionProvider';

export interface WorkspaceNavProps {
  workspaceId: string;
  workspaceName?: string;
  totalDocs?: number;
  totalChunks?: number;
}

export const WorkspaceNav: React.FC<WorkspaceNavProps> = ({
  workspaceId,
  workspaceName = 'Workspace',
  totalDocs = 0,
  totalChunks = 0,
}) => {
  const pathname = usePathname();
  const router = useRouter();
  const sessionContext = useWorkspaceSession();

  const tabs = [
    {
      label: 'Chat',
      href: `/workspaces/${workspaceId}/chat`,
      icon: MessageSquare,
      active: pathname.includes('/chat'),
    },
    {
      label: 'Documents',
      href: `/workspaces/${workspaceId}/documents`,
      icon: FileText,
      active: pathname.includes('/documents'),
    },
    {
      label: 'Analytics',
      href: `/workspaces/${workspaceId}/analytics`,
      icon: BarChart3,
      active: pathname.includes('/analytics'),
    },
  ];

  return (
    <header className="border-b border-outline-variant/60 bg-surface-container-lowest/90 backdrop-blur-md px-4 sm:px-6 py-2.5 flex items-center justify-between gap-4 flex-shrink-0 z-20 h-14 select-none">
      {/* 1. LEFT: Mobile Drawer Toggle, Back Button & Workspace Breadcrumb */}
      <div className="flex items-center gap-3 min-w-0 flex-1 sm:flex-initial">
        {/* Mobile / Tablet Hamburger Toggle */}
        <button
          onClick={() => sessionContext?.setIsMobileDrawerOpen(true)}
          className="lg:hidden p-2 -ml-1 rounded-xl text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
          aria-label="Open navigation drawer"
          title="Open conversation list"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Back Link to All Workspaces */}
        <button
          onClick={() => router.push('/')}
          className="hidden sm:flex items-center justify-center w-8 h-8 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
          title="Back to all workspaces"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>

        {/* Workspace Title & Metadata Badge */}
        <div className="flex items-center gap-2.5 min-w-0">
          <h1 className="text-sm sm:text-base font-bold text-on-surface tracking-tight truncate max-w-[160px] sm:max-w-xs">
            {workspaceName}
          </h1>
          <span className="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full bg-surface-container-high text-[11px] font-semibold text-on-surface-variant border border-outline-variant/50">
            {totalDocs} Docs • {totalChunks} Chunks
          </span>
        </div>
      </div>

      {/* 2. CENTER: Desktop Centered Navigation Hub (Chat | Documents | Analytics) */}
      <nav className="hidden md:flex items-center gap-1.5 p-1 bg-surface-container/80 rounded-xl border border-outline-variant/50 shadow-xs">
        {tabs.map((tab) => (
          <Link
            key={tab.label}
            href={tab.href}
            className={`relative flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold transition-all z-10 ${
              tab.active
                ? 'text-on-primary shadow-xs'
                : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
            }`}
          >
            {tab.active && (
              <motion.div
                layoutId="workspaceActiveCenterTab"
                transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                className="absolute inset-0 bg-primary rounded-lg -z-10 shadow-xs"
              />
            )}
            <tab.icon className="w-4 h-4 flex-shrink-0" />
            <span>{tab.label}</span>
          </Link>
        ))}
      </nav>

      {/* 3. RIGHT: Status Indicator / Mobile Tab Pills */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {/* Mobile Navigation Icons */}
        <div className="flex md:hidden items-center gap-1 bg-surface-container/80 p-0.5 rounded-lg border border-outline-variant/40">
          {tabs.map((tab) => (
            <Link
              key={tab.label}
              href={tab.href}
              className={`p-1.5 rounded-md transition-all ${
                tab.active
                  ? 'bg-primary text-on-primary font-bold shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
              title={tab.label}
            >
              <tab.icon className="w-4 h-4" />
            </Link>
          ))}
        </div>

        {/* Desktop Intelligence Grounding Status Badge */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container text-[11px] font-medium text-on-surface-variant border border-outline-variant/40">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          <span>Hybrid RAG Grounded</span>
        </div>
      </div>
    </header>
  );
};
