'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { MessageSquare, FileText, BarChart3, ArrowLeft, Layers, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';
import { IconButton } from '../primitives';

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

  const tabs = [
    {
      label: 'Chat',
      href: `/workspaces/${workspaceId}/chat`,
      icon: MessageSquare,
      active: pathname.endsWith('/chat'),
    },
    {
      label: 'Documents',
      href: `/workspaces/${workspaceId}/documents`,
      icon: FileText,
      active: pathname.endsWith('/documents'),
    },
    {
      label: 'Analytics',
      href: `/workspaces/${workspaceId}/analytics`,
      icon: BarChart3,
      active: pathname.endsWith('/analytics'),
    },
  ];

  return (
    <header className="border-b border-outline-variant bg-surface-container-lowest/80 backdrop-blur-md px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 flex-shrink-0 z-20">
      {/* Title & Back Link */}
      <div className="flex items-center gap-3">
        <IconButton
          label="Back to workspaces"
          size="sm"
          onClick={() => router.push('/')}
        >
          <ArrowLeft className="w-4 h-4" />
        </IconButton>

        <div>
          <h1 className="text-sm sm:text-base font-bold text-on-surface tracking-tight truncate max-w-xs sm:max-w-md">
            {workspaceName}
          </h1>
          <div className="flex items-center gap-2 text-[11px] text-on-surface-variant">
            <span>{totalDocs} Docs</span>
            <span>•</span>
            <span>{totalChunks} Chunks</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <nav className="flex items-center gap-1 bg-surface-container-low p-1 rounded-xl border border-outline-variant select-none">
        {tabs.map((tab) => (
          <Link
            key={tab.label}
            href={tab.href}
            className={`relative flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors z-10 ${
              tab.active
                ? 'text-on-primary-container font-semibold'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {tab.active && (
              <motion.div
                layoutId="workspaceActiveTab"
                transition={{ type: 'spring', stiffness: 450, damping: 35 }}
                className="absolute inset-0 bg-primary-container rounded-lg -z-10 shadow-xs"
              />
            )}
            <tab.icon className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{tab.label}</span>
          </Link>
        ))}
      </nav>
    </header>
  );
};
