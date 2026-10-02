'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Plus,
  Folder,
  Trash2,
  ArrowRight,
  AlertCircle,
  RefreshCw,
  Search,
  Layers,
  FileText,
} from 'lucide-react';
import { getWorkspaces, createWorkspace, deleteWorkspace, APIError } from '@/lib/api';
import { Button, IconButton, Card, Badge, Modal, Input, Textarea, Spinner } from '@/components/primitives';

interface Workspace {
  workspace_id: string;
  workspace_name: string;
  description?: string;
  total_documents: number;
  total_chunks: number;
  created_at?: string;
}

export default function WorkspacesDashboard() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createDesc, setCreateDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [deleteModalWs, setDeleteModalWs] = useState<Workspace | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchWorkspaces = useCallback(async () => {
    setErrorMessage(null);
    try {
      const data = await getWorkspaces();
      setWorkspaces(data?.workspaces || []);
    } catch (err: unknown) {
      const msg =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to load workspaces';
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;
    const run = async () => {
      if (!isCancelled) await fetchWorkspaces();
    };
    void run();
    return () => {
      isCancelled = true;
    };
  }, [fetchWorkspaces]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createName.trim()) {
      setFormError('Workspace name is required.');
      return;
    }

    setCreating(true);
    setFormError(null);
    try {
      const res = await createWorkspace({
        name: createName.trim(),
        description: createDesc.trim() || undefined,
      });
      setIsCreateOpen(false);
      setCreateName('');
      setCreateDesc('');
      await fetchWorkspaces();
      router.push(`/workspaces/${res.workspace_id}/chat`);
    } catch (err: unknown) {
      const msg =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Could not create workspace';
      setFormError(msg);
    } finally {
      setCreating(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteModalWs) return;

    setDeleting(true);
    try {
      await deleteWorkspace(deleteModalWs.workspace_id);
      setDeleteModalWs(null);
      await fetchWorkspaces();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete workspace';
      setErrorMessage(msg);
    } finally {
      setDeleting(false);
    }
  };

  const filteredWorkspaces = workspaces.filter(
    (ws) =>
      ws.workspace_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ws.description && ws.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="flex-1 overflow-y-auto p-6 sm:p-10 max-w-7xl mx-auto w-full">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
            Workspaces
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1">
            Isolated contextual knowledge bases powered by hybrid FAISS & BM25 indices.
          </p>
        </div>

        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => {
            setFormError(null);
            setIsCreateOpen(true);
          }}
        >
          New Workspace
        </Button>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-error-container/20 border border-error/30 flex items-center justify-between text-error text-xs font-medium animate-in fade-in duration-200">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <Button size="sm" variant="ghost" onClick={fetchWorkspaces}>
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </Button>
        </div>
      )}

      {/* Search Filter Bar */}
      {workspaces.length > 0 && (
        <div className="mb-6 max-w-md">
          <Input
            placeholder="Search workspaces by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            iconPrefix={<Search className="w-4 h-4" />}
          />
        </div>
      )}

      {/* Grid Content */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center gap-3">
          <Spinner size="lg" />
          <p className="text-xs text-on-surface-variant">Connecting to intelligence engine...</p>
        </div>
      ) : workspaces.length === 0 ? (
        <Card className="text-center py-16">
          <Folder className="w-12 h-12 text-on-surface-variant opacity-40 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-on-surface">No workspaces yet</h3>
          <p className="text-xs text-on-surface-variant max-w-sm mx-auto mt-1 leading-relaxed">
            Create your first workspace to upload course material, research papers, or documentation and begin asking grounded questions.
          </p>
          <Button
            className="mt-6"
            variant="primary"
            icon={<Plus className="w-4 h-4" />}
            onClick={() => setIsCreateOpen(true)}
          >
            Create your first workspace
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredWorkspaces.map((ws) => (
            <div
              key={ws.workspace_id}
              onClick={() => router.push(`/workspaces/${ws.workspace_id}/chat`)}
              className="group relative flex flex-col justify-between p-5 rounded-2xl border border-outline-variant bg-surface-container-low hover:bg-surface-container hover:border-outline transition-all duration-200 cursor-pointer shadow-xs hover:shadow-md"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="w-9 h-9 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center shadow-xs flex-shrink-0 group-hover:scale-105 transition-transform">
                    <Folder className="w-4 h-4 text-primary" />
                  </div>
                  <IconButton
                    label="Delete workspace"
                    variant="danger"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteModalWs(ws);
                    }}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </IconButton>
                </div>

                <h3 className="text-sm font-bold text-on-surface tracking-tight truncate group-hover:text-primary transition-colors">
                  {ws.workspace_name}
                </h3>
                <p className="text-xs text-on-surface-variant line-clamp-2 mt-1 min-h-[32px] leading-relaxed">
                  {ws.description || 'No description provided.'}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-outline-variant/60 flex items-center justify-between text-[11px] text-on-surface-variant">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    <span>{ws.total_documents} docs</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5" />
                    <span>{ws.total_chunks} chunks</span>
                  </span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all text-primary" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Workspace Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create New Workspace"
        description="Initialize an isolated context container for your documents."
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <Input
            label="Workspace Name"
            placeholder="e.g. Molecular Biology 101"
            value={createName}
            onChange={(e) => setCreateName(e.target.value)}
            error={formError || undefined}
            autoFocus
          />

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-on-surface select-none tracking-wide">
              Description (Optional)
            </label>
            <div className="border border-outline-variant rounded-lg p-2.5 bg-surface-container-low">
              <Textarea
                placeholder="What topics or textbooks will be indexed here?"
                value={createDesc}
                onChange={(e) => setCreateDesc(e.target.value)}
                maxHeight={120}
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsCreateOpen(false)}
              disabled={creating}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" loading={creating}>
              Create Workspace
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Workspace Modal */}
      <Modal
        isOpen={!!deleteModalWs}
        onClose={() => setDeleteModalWs(null)}
        title="Delete Workspace"
        description="Permanently delete this workspace and all indexed vectors?"
      >
        <div className="space-y-4">
          <p className="text-xs text-on-surface-variant leading-relaxed">
            Deleting <span className="font-semibold text-on-surface">{deleteModalWs?.workspace_name}</span> will remove all associated documents, {deleteModalWs?.total_chunks} chunks, FAISS vector embeddings, and conversation history.
          </p>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteModalWs(null)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleConfirmDelete}
              loading={deleting}
            >
              Delete Permanently
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
