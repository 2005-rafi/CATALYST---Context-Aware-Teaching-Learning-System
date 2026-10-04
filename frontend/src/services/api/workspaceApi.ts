/**
 * Workspace API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import {
  WorkspaceListResult,
  WorkspaceResult,
  CreateWorkspacePayload,
} from '@/types/workspace';

export const getWorkspaces = () =>
  fetchWrapper<WorkspaceListResult>(ENDPOINTS.WORKSPACES.LIST, { retries: 1 });

export const getWorkspace = (id: string) =>
  fetchWrapper<WorkspaceResult>(ENDPOINTS.WORKSPACES.DETAIL(id));

export const createWorkspace = (data: CreateWorkspacePayload) =>
  fetchWrapper<WorkspaceResult>(ENDPOINTS.WORKSPACES.CREATE, {
    method: 'POST',
    body: JSON.stringify({ workspace_name: data.name, description: data.description }),
  });

export const deleteWorkspace = (id: string) =>
  fetchWrapper<null>(ENDPOINTS.WORKSPACES.DELETE(id), { method: 'DELETE' });
