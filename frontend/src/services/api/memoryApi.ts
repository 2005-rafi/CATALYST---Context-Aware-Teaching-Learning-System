/**
 * Memory Profile API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { UserMemoryProfile } from '@/types/session';

export const getUserProfile = (workspaceId: string) =>
  fetchWrapper<UserMemoryProfile>(ENDPOINTS.MEMORY.PROFILE(workspaceId));

export const resetUserProfile = (workspaceId: string) =>
  fetchWrapper<null>(ENDPOINTS.MEMORY.RESET_PROFILE(workspaceId), { method: 'DELETE' });
