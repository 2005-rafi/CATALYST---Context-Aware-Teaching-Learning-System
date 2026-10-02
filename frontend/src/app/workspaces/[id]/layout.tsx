'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';
import { MessageSquare, FileText, BarChart2, ArrowLeft } from 'lucide-react';
import { getWorkspace, WorkspaceResult } from '@/lib/api';

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const params = useParams();
  const workspaceId = params.id as string;
  const [workspace, setWorkspace] = useState<WorkspaceResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchWS() {
      try {
        const ws = await getWorkspace(workspaceId);
        setWorkspace(ws);
      } catch (err: unknown) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.warn(`[Network Warning] Failed to fetch workspace detail: ${error.message}`);
      } finally {
        setLoading(false);
      }
    }
    if (workspaceId) void fetchWS();
  }, [workspaceId]);

  const tabs = [
    { name: 'Chat', href: `/workspaces/${workspaceId}/chat`, icon: MessageSquare },
    { name: 'Documents', href: `/workspaces/${workspaceId}/documents`, icon: FileText },
    { name: 'Analytics', href: `/workspaces/${workspaceId}/analytics`, icon: BarChart2 },
  ];

  return (
    <div className="flex flex-col h-full relative">
      {/* Header */}
      <header className="bg-surface-container border-b border-border flex items-center px-6 h-16 shrink-0 z-10 sticky top-0">
        <div className="flex items-center flex-1">
          <Link href="/" className="mr-4 text-on-surface-variant hover:text-on-surface transition-colors p-2 -ml-2 rounded-full hover:bg-surface-variant">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          
          {loading ? (
            <div className="h-6 w-48 bg-surface-variant animate-pulse rounded"></div>
          ) : (
            <h2 className="text-xl font-bold truncate pr-4 text-on-surface">{workspace?.workspace_name || 'Unknown Workspace'}</h2>
          )}
        </div>
        
        {/* Tabs */}
        <nav className="flex items-center space-x-1 h-full pt-2">
          {tabs.map((tab) => {
            const isActive = pathname === tab.href || pathname.startsWith(tab.href + '/');
            return (
              <Link
                key={tab.name}
                href={tab.href}
                className={`flex items-center gap-2 px-4 h-full border-b-2 font-medium text-sm transition-colors ${
                  isActive 
                    ? 'border-primary text-primary' 
                    : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-border'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </Link>
            );
          })}
        </nav>
      </header>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {children}
      </div>
    </div>
  );
}
