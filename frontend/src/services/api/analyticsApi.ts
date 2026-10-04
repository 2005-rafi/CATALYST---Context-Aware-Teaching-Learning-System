/**
 * Analytics API Service
 */

import { ENDPOINTS } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { AnalyticsResult, DetailedAnalyticsResult } from '@/types/analytics';

export const getAnalytics = (workspaceId: string) =>
  fetchWrapper<AnalyticsResult>(ENDPOINTS.ANALYTICS.BY_WORKSPACE(workspaceId));

export const getDetailedAnalytics = (workspaceId: string, days: number = 14) =>
  fetchWrapper<DetailedAnalyticsResult>(ENDPOINTS.ANALYTICS.DETAILED(workspaceId, days));
