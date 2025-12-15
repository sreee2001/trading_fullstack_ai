/**
 * Forecast Service
 * 
 * Service for interacting with the forecast API endpoint.
 */

import apiClient from '../lib/apiClient';
import type { ForecastRequest, ForecastResponse } from '../types/api';

export const forecastService = {
  /**
   * Generate price forecast for a commodity
   */
  async generateForecast(request: ForecastRequest): Promise<ForecastResponse> {
    const response = await apiClient.post<ForecastResponse>('/api/v1/forecast', request);
    return response.data;
  },
};

