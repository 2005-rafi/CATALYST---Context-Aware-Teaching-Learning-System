/**
 * System Health & Diagnostics API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { SystemHealthResult } from '@/types/api';

export const getSystemHealth = () =>
  fetchWrapper<SystemHealthResult>(ENDPOINTS.SYSTEM.HEALTH);
