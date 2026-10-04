/**
 * Document API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { DocumentListResult, DocumentUploadResponse } from '@/types/document';

export const getDocumentsByWorkspace = (workspaceId: string) =>
  fetchWrapper<DocumentListResult>(ENDPOINTS.DOCUMENTS.BY_WORKSPACE(workspaceId));

export const uploadDocument = (workspaceId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('workspace_id', workspaceId);
  return fetchWrapper<DocumentUploadResponse>(ENDPOINTS.DOCUMENTS.UPLOAD, {
    method: 'POST',
    body: formData,
  });
};

export const deleteDocument = (id: string) =>
  fetchWrapper<null>(ENDPOINTS.DOCUMENTS.DELETE(id), { method: 'DELETE' });
