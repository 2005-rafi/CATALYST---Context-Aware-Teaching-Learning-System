'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { WorkspaceNav } from '@/components/layout/WorkspaceNav';
import { useWorkspaceSession } from '@/components/providers/WorkspaceSessionProvider';

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const workspaceId = params.id as string;
  const sessionContext = useWorkspaceSession();
  const workspace = sessionContext?.workspace;

  return (
    <div className="flex flex-col h-full relative overflow-hidden bg-background">
      <WorkspaceNav
        workspaceId={workspaceId}
        workspaceName={workspace?.workspace_name}
        totalDocs={workspace?.total_documents}
        totalChunks={workspace?.total_chunks}
      />
      <div className="flex-1 overflow-hidden relative flex flex-col">
        {children}
      </div>
    </div>
  );
}
