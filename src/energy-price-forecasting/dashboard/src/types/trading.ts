/**
 * Trading Signal Types
 * 
 * TypeScript interfaces for trading signals and strategies.
 */

export type SignalType = 'buy' | 'sell' | 'hold';

export interface TradingSignal {
  date: string; // YYYY-MM-DD
  signal: SignalType;
  price: number;
  confidence?: number;
  reason?: string;
}

export interface SignalStrategy {
  name: string;
  description: string;
  parameters?: Record<string, unknown>;
}

// Re-export PricePoint from api types for convenience
export type { PricePoint } from './api';

