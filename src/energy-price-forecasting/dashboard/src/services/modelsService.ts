/**
 * Models Service
 * 
 * Service for interacting with the models API endpoint.
 */

import apiClient from '../lib/apiClient';
import type { ModelsListResponse } from '../types/api';

export const modelsService = {
  /**
   * Get list of all available models
   */
  async getAllModels(commodity?: string): Promise<ModelsListResponse> {
    const params = commodity ? `?commodity=${commodity}` : '';
    const response = await apiClient.get<ModelsListResponse>(`/api/v1/models${params}`);
    return response.data;
  },
};

