'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Plus, Folder, Trash2, Loader2, ArrowRight, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { getWorkspaces, createWorkspace, deleteWorkspace } from '@/lib/api';

interface Workspace {
  workspace_id: string;
  workspace_name: string;
  description?: string;
  total_documents: number;
  total_chunks: number;
  created_at?: string;
}

export default function WorkspacesDashboard() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [newWorkspaceDesc, setNewWorkspaceDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchWorkspaces = useCallback(async () => {
    setErrorMessage(null);
    try {
      const data = await getWorkspaces();
      setWorkspaces(data?.workspaces || []);
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      setErrorMessage(err.message || 'Failed to load workspaces from backend.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    const load = async () => {
      if (!isCancelled) {
        await fetchWorkspaces();
      }
    };
    void load();
    return () => {
      isCancelled = true;
    };
  }, [fetchWorkspaces]);

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWorkspaceName.trim()) {
      setFormError('Workspace name cannot be blank.');
      return;
    }

    setCreating(true);
    setFormError(null);
    try {
      await createWorkspace({ name: newWorkspaceName.trim(), description: newWorkspaceDesc.trim() });
      setIsCreateModalOpen(false);
      setNewWorkspaceName('');
      setNewWorkspaceDesc('');
      await fetchWorkspaces();
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      setFormError(err.message || 'Failed to create workspace.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteWorkspace = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this workspace and all its indexed vectors?')) return;
    
    try {
      await deleteWorkspace(id);
      await fetchWorkspaces();
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      setErrorMessage(err.message || 'Failed to delete workspace.');
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Workspaces</h1>
          <p className="text-on-surface-variant mt-1">Manage your intelligent document contexts and retrieval indexes.</p>
        </div>
        <button 
          onClick={() => {
            setFormError(null);
            setIsCreateModalOpen(true);
          }}
          className="bg-primary hover:opacity-90 text-primary-foreground px-4 py-2.5 rounded-lg font-medium flex items-center gap-2 transition-opacity shadow-sm"
        >
          <Plus className="w-5 h-5" />
          <span>New Workspace</span>
        </button>
      </div>

      {/* Error Alert Banner */}
      {errorMessage && (
        <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center justify-between text-rose-500 shadow-sm">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-medium">{errorMessage}</p>
          </div>
          <button
            onClick={fetchWorkspaces}
            className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-rose-500/20 hover:bg-rose-500/30 text-xs font-semibold uppercase tracking-wider transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col justify-center items-center h-64 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-sm text-on-surface-variant">Connecting to backend platform...</p>
        </div>
      ) : workspaces.length === 0 ? (
        <div className="text-center py-20 bg-surface-container border border-dashed border-border rounded-xl">
          <Folder className="w-12 h-12 text-on-surface-variant opacity-50 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground">No Workspaces Found</h3>
          <p className="text-on-surface-variant mt-1 max-w-sm mx-auto text-sm">
            Get started by creating your first workspace to upload documents and begin intelligent hybrid retrieval.
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
          >
            <Plus className="w-4 h-4" />
            <span>Create your first workspace</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workspaces.map((ws) => (
            <Link
              key={ws.workspace_id}
              href={`/workspaces/${ws.workspace_id}`}
              className="group p-6 bg-surface border border-border rounded-xl hover:border-primary transition-all duration-300 shadow-sm hover:shadow-md flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="p-3 bg-primary-container rounded-lg group-hover:scale-105 transition-transform duration-200">
                    <Layers className="w-6 h-6 text-on-primary-container" />
                  </div>
                  <button
                    onClick={(e) => handleDeleteWorkspace(e, ws.workspace_id)}
                    className="opacity-0 group-hover:opacity-100 p-2 text-on-surface-variant hover:text-rose-500 transition-all rounded-md hover:bg-surface-variant"
                    title="Delete workspace"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <h3 className="text-lg font-bold text-foreground mt-4 group-hover:text-primary transition-colors">
                  {ws.workspace_name}
                </h3>
                <p className="text-sm text-on-surface-variant mt-1 line-clamp-2">
                  {ws.description || 'No description provided.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-border flex items-center justify-between text-xs text-on-surface-variant">
                <div className="flex items-center gap-3">
                  <span>{ws.total_documents || 0} docs</span>
                  <span>•</span>
                  <span>{ws.total_chunks || 0} chunks</span>
                </div>
                <div className="flex items-center gap-1 font-medium text-primary group-hover:translate-x-1 transition-transform">
                  <span>Open</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Create Workspace Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 shadow-xl animate-in fade-in zoom-in-95 duration-200">
            <h2 className="text-xl font-bold text-foreground mb-4">Create New Workspace</h2>
            
            {formError && (
              <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-xs text-rose-500 font-medium">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateWorkspace} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1.5">
                  Workspace Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Legal Contracts 2026"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-border bg-surface-container text-foreground text-sm focus:outline-none focus:border-primary transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1.5">
                  Description
                </label>
                <textarea
                  placeholder="Brief description of the documents and use-case..."
                  rows={3}
                  value={newWorkspaceDesc}
                  onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-border bg-surface-container text-foreground text-sm focus:outline-none focus:border-primary transition-colors resize-none"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-border">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 rounded-lg border border-border text-on-surface-variant hover:bg-surface-variant text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-primary hover:opacity-90 text-primary-foreground px-5 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-opacity disabled:opacity-50"
                >
                  {creating && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>{creating ? 'Creating...' : 'Create Workspace'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
