/**
 * API Types
 * 
 * TypeScript interfaces for API request/response models.
 */

// Forecast Types
export interface ForecastRequest {
  commodity: 'WTI' | 'BRENT' | 'NG';
  horizon: number; // 1-30 days
  start_date: string; // YYYY-MM-DD
}

export interface Prediction {
  date: string; // YYYY-MM-DD
  price: number;
  confidence_lower: number;
  confidence_upper: number;
}

export interface ForecastResponse {
  commodity: string;
  forecast_date: string;
  horizon: number;
  predictions: Prediction[];
  model_info?: {
    model_type?: string;
    version?: string;
  };
}

// Historical Data Types
export interface HistoricalDataRequest {
  commodity: 'WTI' | 'BRENT' | 'NG';
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
  limit?: number;
  offset?: number;
  source?: string;
}

export interface PricePoint {
  timestamp: string;
  price: number;
  volume?: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  source?: string;
}

export interface HistoricalDataResponse {
  commodity: string;
  start_date: string;
  end_date: string;
  data: PricePoint[];
  total_count: number;
  limit: number;
  offset: number;
}

// Model Types
export interface ModelMetrics {
  rmse?: number;
  mae?: number;
  mape?: number;
  r2?: number;  // API uses r2, not r_squared
  r_squared?: number;  // Keep for backward compatibility
  directional_accuracy?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  max_drawdown?: number;
  total_return?: number;
  win_rate?: number;
}

export interface ModelInfo {
  model_id: string;
  model_name?: string;
  commodity: string;
  model_type: string;
  version: string;
  stage: string;
  training_date?: string | null;
  created_at?: string | null;
  metrics?: ModelMetrics | null;
  tags?: Record<string, string> | null;
  run_id?: string | null;
  experiment_id?: string | null;
  description?: string | null;
  parameters?: Record<string, unknown>;
}

export interface ModelsListResponse {
  models: ModelInfo[];
  total_count: number;
  commodity_filter?: string | null;
}

// Backtest Types
export interface BacktestRequest {
  model_id: string;
  start_date: string; // YYYY-MM-DD
  end_date: string; // YYYY-MM-DD
  initial_capital?: number;
  commission?: number;
  slippage?: number;
  strategy_params?: Record<string, unknown>;
}

export interface BacktestMetrics {
  total_return?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  total_trades?: number;
  rmse?: number;
  mae?: number;
  mape?: number;
  r_squared?: number;
  directional_accuracy?: number;
  initial_capital?: number;
  final_capital?: number;
  cumulative_pnl?: number;
}

export interface Trade {
  entry_idx: number;
  exit_idx: number;
  entry_price: number;
  exit_price: number;
  position: number; // 1 = long, -1 = short
  pnl?: number; // Fraction
  pnl_dollars?: number; // Dollars
  capital_after?: number;
  timestamp?: string;
}

export interface BacktestResponse {
  model_id: string;
  start_date: string;
  end_date: string;
  metrics: BacktestMetrics;
  num_trades: number;
  trades: Trade[];
  equity_curve?: number[]; // Array of equity values
  initial_capital?: number;
  final_capital?: number;
}

