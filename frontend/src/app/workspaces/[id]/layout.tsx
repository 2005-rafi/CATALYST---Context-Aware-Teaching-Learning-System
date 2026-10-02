'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { getWorkspace, WorkspaceResult } from '@/lib/api';
import { WorkspaceNav } from '@/components/layout/WorkspaceNav';

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const workspaceId = params.id as string;
  const [workspace, setWorkspace] = useState<WorkspaceResult | null>(null);

  useEffect(() => {
    let isCancelled = false;
    async function fetchWS() {
      try {
        const ws = await getWorkspace(workspaceId);
        if (!isCancelled) {
          setWorkspace(ws);
        }
      } catch (err: unknown) {
        console.warn('Failed to fetch workspace detail:', err);
      }
    }
    if (workspaceId) void fetchWS();
    return () => {
      isCancelled = true;
    };
  }, [workspaceId]);

  return (
    <div className="flex flex-col h-full relative overflow-hidden bg-background">
      <WorkspaceNav
        workspaceId={workspaceId}
        workspaceName={workspace?.workspace_name}
      />
      <div className="flex-1 overflow-hidden relative flex flex-col">
        {children}
      </div>
    </div>
  );
}
