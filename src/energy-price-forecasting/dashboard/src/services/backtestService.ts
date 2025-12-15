/**
 * Backtest Service
 * 
 * Service for interacting with the backtest API endpoint.
 */

import apiClient from '../lib/apiClient';
import type { BacktestRequest, BacktestResponse } from '../types/api';

export const backtestService = {
  /**
   * Run a backtest for a model
   */
  async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
    const response = await apiClient.post<BacktestResponse>('/api/v1/backtest', request);
    return response.data;
  },
};

