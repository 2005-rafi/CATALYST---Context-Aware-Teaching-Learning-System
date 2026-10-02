'use client';

import { useState, useEffect, useRef, use, useCallback } from 'react';
import { UploadCloud, File as FileIcon, Trash2, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { getDocumentsByWorkspace, uploadDocument, deleteDocument, DocumentStatus } from '@/lib/api';

export default function DocumentsPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const workspaceId = unwrappedParams.id;
  
  const [documents, setDocuments] = useState<DocumentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = useCallback(async () => {
    try {
      const docs = await getDocumentsByWorkspace(workspaceId);
      setDocuments(docs.documents || []);
      return docs.documents || [];
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.warn(`[Network Warning] Failed to fetch docs: ${err.message}`);
      return [];
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    let isCancelled = false;
    const initialLoad = async () => {
      if (!isCancelled) {
        await fetchDocs();
      }
    };
    void initialLoad();

    const interval = setInterval(async () => {
      if (isCancelled) return;
      const docs = await fetchDocs();
      const stillProcessing = docs?.some((d) => d.processing_status === 'processing');
      if (!stillProcessing) clearInterval(interval);
    }, 3000);

    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [fetchDocs]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(workspaceId, file);
      await fetchDocs();
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.warn(`[Network Warning] Failed to upload doc: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) await handleUpload(file);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await handleUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document from the knowledge base?')) return;
    try {
      await deleteDocument(documentId);
      await fetchDocs();
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.warn(`[Network Warning] Failed to delete doc: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto flex flex-col h-full">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
          <p className="text-on-surface-variant mt-1">Upload documents to expand the context.</p>
        </div>
      </div>

      {/* Upload Zone */}
      <div 
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed border-border rounded-xl p-10 text-center cursor-pointer transition-all duration-300 ${uploading ? 'bg-surface-variant cursor-not-allowed opacity-70' : 'hover:bg-surface-variant hover:border-primary'}`}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          onChange={handleFileSelect}
          accept=".pdf,.docx,.txt" 
        />
        {uploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
            <p className="font-medium text-primary">Uploading & Ingesting...</p>
            <p className="text-sm text-on-surface-variant mt-1">Extracting text, chunking, and vector indexing.</p>
          </div>
        ) : (
          <div className="flex flex-col items-center group">
            <div className="w-16 h-16 bg-surface-container rounded-full flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110 shadow-sm">
              <UploadCloud className="w-8 h-8 text-primary" />
            </div>
            <p className="font-medium text-lg text-on-surface">Click or drag file to upload</p>
            <p className="text-sm text-on-surface-variant mt-1">Supports PDF, DOCX, and TXT</p>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="mt-8 flex-1 overflow-y-auto pr-2 pb-8">
        <h3 className="font-semibold mb-4 text-lg text-on-surface">Uploaded Files ({documents.length})</h3>
        
        {loading ? (
          <div className="flex justify-center p-8">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 bg-surface-container border border-border rounded-xl text-on-surface-variant shadow-sm">
            No documents uploaded yet.
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div key={doc.document_id} className="flex items-center justify-between p-5 bg-surface border border-border rounded-xl hover:border-primary transition-all duration-300 shadow-sm hover:shadow-md">
                <div className="flex items-center gap-4">
                  <div className="bg-primary-container p-3 rounded-lg">
                    <FileIcon className="w-6 h-6 text-on-primary-container" />
                  </div>
                  <div>
                    <h4 className="font-medium text-on-surface">{doc.file_name}</h4>
                    <div className="flex items-center gap-3 text-xs text-on-surface-variant mt-1">
                      <span>{(doc.file_size_mb || 0).toFixed(2)} MB</span>
                      <span>•</span>
                      <span>{doc.total_chunks} chunks</span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(doc.created_at))} ago</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-6">
                  {doc.processing_status === 'completed' && (
                    <span className="flex items-center gap-1.5 text-sm text-on-primary-container font-medium px-3 py-1 bg-primary-container rounded-full">
                      Ready
                    </span>
                  )}
                  {doc.processing_status === 'processing' && (
                    <span className="flex items-center gap-1.5 text-sm text-amber-500 font-medium px-3 py-1 bg-amber-500/10 rounded-full">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Indexing...
                    </span>
                  )}
                  {doc.processing_status === 'failed' && (
                    <span className="flex items-center gap-1.5 text-sm text-rose-500 font-medium px-3 py-1 bg-rose-500/10 rounded-full">
                      Failed
                    </span>
                  )}

                  <button 
                    onClick={() => handleDelete(doc.document_id)}
                    className="text-on-surface-variant hover:text-rose-500 p-2 rounded-lg hover:bg-surface-container transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
