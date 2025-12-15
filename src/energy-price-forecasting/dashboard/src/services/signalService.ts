/**
 * Signal Service
 * 
 * Service for generating trading signals from predictions and prices.
 * This is a client-side implementation that mimics the backend signal generation logic.
 */

import type { TradingSignal, SignalType, PricePoint } from '../types/trading';
import type { Prediction as ApiPrediction } from '../types/api';

/**
 * Generate trading signals based on predictions and historical prices
 */
export const generateSignals = (
  predictions: ApiPrediction[],
  historicalPrices: PricePoint[],
  strategy: 'threshold' | 'momentum' | 'mean_reversion' = 'threshold',
  threshold: number = 0.02
): TradingSignal[] => {
  const signals: TradingSignal[] = [];
  
  if (predictions.length === 0 || historicalPrices.length === 0) {
    return signals;
  }

  // Create a price map for quick lookup
  const priceMap = new Map<string, number>();
  historicalPrices.forEach((point) => {
    const date = new Date(point.timestamp).toISOString().split('T')[0];
    priceMap.set(date, point.price);
  });

  // Get the last historical price for comparison
  const lastHistoricalPrice = historicalPrices[historicalPrices.length - 1]?.price || 0;

  predictions.forEach((pred, index) => {
    let signal: SignalType = 'hold';
    let reason = '';

    if (strategy === 'threshold') {
      // Threshold strategy: Buy if predicted price increase > threshold, Sell if decrease > threshold
      const priceChange = (pred.price - lastHistoricalPrice) / lastHistoricalPrice;
      
      if (priceChange > threshold) {
        signal = 'buy';
        reason = `Predicted increase of ${(priceChange * 100).toFixed(2)}%`;
      } else if (priceChange < -threshold) {
        signal = 'sell';
        reason = `Predicted decrease of ${(Math.abs(priceChange) * 100).toFixed(2)}%`;
      } else {
        signal = 'hold';
        reason = `Price change within threshold (${(priceChange * 100).toFixed(2)}%)`;
      }
    } else if (strategy === 'momentum') {
      // Momentum strategy: Compare with previous prediction
      if (index > 0) {
        const prevPred = predictions[index - 1];
        const momentum = pred.price - prevPred.price;
        
        if (momentum > 0) {
          signal = 'buy';
          reason = 'Positive momentum detected';
        } else if (momentum < 0) {
          signal = 'sell';
          reason = 'Negative momentum detected';
        }
      }
    } else if (strategy === 'mean_reversion') {
      // Mean reversion: Buy if price below mean, Sell if above mean
      const prices = historicalPrices.map((p) => p.price);
      const mean = prices.reduce((sum, p) => sum + p, 0) / prices.length;
      
      if (pred.price < mean * 0.95) {
        signal = 'buy';
        reason = 'Price below mean (oversold)';
      } else if (pred.price > mean * 1.05) {
        signal = 'sell';
        reason = 'Price above mean (overbought)';
      }
    }

    // Only add non-hold signals
    if (signal !== 'hold') {
      signals.push({
        date: pred.date,
        signal,
        price: pred.price,
        confidence: pred.confidence_upper - pred.confidence_lower < pred.price * 0.1 ? 0.8 : 0.5,
        reason,
      });
    }
  });

  return signals;
};

