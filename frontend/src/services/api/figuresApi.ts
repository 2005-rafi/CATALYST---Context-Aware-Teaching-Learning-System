/**
 * Figures API Service (Visual RAG)
 */

import { ENDPOINTS, API_BASE_URL } from '@/config/endpoints';
import { fetchWrapper } from './client';
import { FigureReference } from '@/types/figure';

export const getFiguresByWorkspace = (workspaceId: string) =>
  fetchWrapper<FigureReference[]>(ENDPOINTS.FIGURES.BY_WORKSPACE(workspaceId));

export const getFigurePreviewUrl = (figureId: string) =>
  `${API_BASE_URL}${ENDPOINTS.FIGURES.PREVIEW(figureId)}`;
