/**
 * Historical Data Service
 * 
 * Service for interacting with the historical data API endpoint.
 */

import apiClient from '../lib/apiClient';
import type { HistoricalDataRequest, HistoricalDataResponse } from '../types/api';

export const historicalService = {
  /**
   * Get historical price data for a commodity
   */
  async getHistoricalData(request: HistoricalDataRequest): Promise<HistoricalDataResponse> {
    const params = new URLSearchParams({
      commodity: request.commodity,
      start_date: request.start_date,
      end_date: request.end_date,
      limit: String(request.limit || 1000),
      offset: String(request.offset || 0),
    });
    
    if (request.source) {
      params.append('source', request.source);
    }
    
    const response = await apiClient.get<HistoricalDataResponse>(
      `/api/v1/historical?${params.toString()}`
    );
    return response.data;
  },
};

