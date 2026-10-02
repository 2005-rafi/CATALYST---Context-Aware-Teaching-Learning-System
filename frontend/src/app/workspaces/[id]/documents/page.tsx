'use client';

import React, { useState, useEffect, useCallback, use } from 'react';
import {
  UploadCloud,
  FileText,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Clock,
  RefreshCw,
} from 'lucide-react';
import {
  getDocumentsByWorkspace,
  uploadDocument,
  deleteDocument,
  DocumentStatus,
  APIError,
} from '@/lib/api';
import { Button, IconButton, Badge, Card, Modal, Spinner } from '@/components/primitives';

export default function DocumentsPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;

  const [documents, setDocuments] = useState<DocumentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [deleteModalDoc, setDeleteModalDoc] = useState<DocumentStatus | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchDocs = useCallback(async () => {
    try {
      const res = await getDocumentsByWorkspace(workspaceId);
      setDocuments(res.documents || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch documents';
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    let isCancelled = false;
    const run = async () => {
      if (!isCancelled) await fetchDocs();
    };
    void run();
    return () => {
      isCancelled = true;
    };
  }, [fetchDocs]);

  // Polling for documents in 'processing' status
  useEffect(() => {
    const hasProcessing = documents.some(
      (d) => d.processing_status === 'processing' || d.processing_status === 'pending'
    );
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      void fetchDocs();
    }, 3000);

    return () => clearInterval(interval);
  }, [documents, fetchDocs]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress(`Uploading ${file.name}...`);
    setErrorMessage(null);

    try {
      await uploadDocument(workspaceId, file);
      setUploadProgress('Extracting and indexing chunks...');
      await fetchDocs();
    } catch (err: unknown) {
      const msg =
        err instanceof APIError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Failed to upload document';
      setErrorMessage(msg);
    } finally {
      setUploading(false);
      setUploadProgress(null);
      e.target.value = '';
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteModalDoc) return;

    setDeleting(true);
    try {
      await deleteDocument(deleteModalDoc.document_id);
      setDeleteModalDoc(null);
      await fetchDocs();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete document';
      setErrorMessage(msg);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 sm:p-8 max-w-6xl mx-auto w-full">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-xl font-bold text-on-surface tracking-tight">Documents</h2>
          <p className="text-xs text-on-surface-variant mt-1">
            Ingest and manage files for hybrid semantic vector search and BM25 lexical indexing.
          </p>
        </div>

        <Button
          size="sm"
          variant="outline"
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          onClick={fetchDocs}
        >
          Refresh
        </Button>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-xl bg-error-container/20 border border-error/30 flex items-center justify-between text-error text-xs font-medium animate-in fade-in duration-200">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="hover:underline font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div className="mb-8">
        <label className="relative flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-outline-variant hover:border-primary bg-surface-container-low hover:bg-surface-container transition-all cursor-pointer group">
          <div className="w-12 h-12 rounded-xl bg-primary-container text-on-primary-container flex items-center justify-center mb-3 group-hover:scale-105 transition-transform shadow-xs">
            {uploading ? (
              <Spinner size="md" />
            ) : (
              <UploadCloud className="w-6 h-6 text-primary" />
            )}
          </div>

          <span className="text-sm font-semibold text-on-surface">
            {uploading ? uploadProgress : 'Click or drag documents to upload'}
          </span>
          <span className="text-xs text-on-surface-variant mt-1">
            Supports PDF, TXT, DOCX, and MD files up to 50MB
          </span>

          <input
            type="file"
            accept=".pdf,.txt,.docx,.md"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
      </div>

      {/* Documents List */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-3 select-none">
          Workspace Files ({documents.length})
        </h3>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-2">
            <Spinner size="md" />
            <p className="text-xs text-on-surface-variant">Loading workspace documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <Card className="text-center py-12">
            <FileText className="w-10 h-10 text-on-surface-variant opacity-40 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-on-surface">No documents uploaded</h4>
            <p className="text-xs text-on-surface-variant max-w-sm mx-auto mt-1">
              Upload PDF or text documents above to parse text, compute embeddings, and enable contextual RAG answering.
            </p>
          </Card>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-outline-variant bg-surface-container-low">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-container-high text-on-surface-variant font-medium border-b border-outline-variant">
                <tr>
                  <th className="py-3 px-4">Document</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/50">
                {documents.map((doc) => {
                  const isProcessing =
                    doc.processing_status === 'processing' || doc.processing_status === 'pending';
                  const isFailed = doc.processing_status === 'failed';

                  return (
                    <tr
                      key={doc.document_id}
                      className="hover:bg-surface-container/60 transition-colors"
                    >
                      <td className="py-3.5 px-4 font-medium text-on-surface flex items-center gap-2.5">
                        <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                        <span className="truncate max-w-xs" title={doc.file_name}>
                          {doc.file_name}
                        </span>
                      </td>

                      <td className="py-3.5 px-4 text-on-surface-variant font-mono">
                        {doc.file_size_mb < 0.1
                          ? `${(doc.file_size_mb * 1024).toFixed(0)} KB`
                          : `${doc.file_size_mb.toFixed(2)} MB`}
                      </td>

                      <td className="py-3.5 px-4">
                        <Badge variant="neutral" size="sm">
                          {doc.total_chunks} chunks
                        </Badge>
                      </td>

                      <td className="py-3.5 px-4">
                        {isProcessing ? (
                          <div className="flex items-center gap-1.5 text-primary">
                            <Clock className="w-3.5 h-3.5 animate-spin" />
                            <span className="capitalize">{doc.processing_status}...</span>
                          </div>
                        ) : isFailed ? (
                          <div className="flex items-center gap-1.5 text-error">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span>Failed</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1.5 text-emerald-500">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Indexed</span>
                          </div>
                        )}
                      </td>

                      <td className="py-3.5 px-4 text-right">
                        <IconButton
                          label="Delete document"
                          variant="danger"
                          size="sm"
                          onClick={() => setDeleteModalDoc(doc)}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </IconButton>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteModalDoc}
        onClose={() => setDeleteModalDoc(null)}
        title="Delete Document"
        description="Are you sure you want to delete this document?"
      >
        <div className="space-y-4">
          <p className="text-xs text-on-surface-variant leading-relaxed">
            Deleting <span className="font-semibold text-on-surface">{deleteModalDoc?.file_name}</span> will permanently purge all {deleteModalDoc?.total_chunks} indexed vector chunks and FTS lexical tokens.
          </p>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteModalDoc(null)}
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
