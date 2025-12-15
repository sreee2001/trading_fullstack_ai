/**
 * Combined Chart Component
 * 
 * Displays both historical prices and forecast predictions on the same chart.
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
} from 'recharts';
import type { PricePoint, Prediction } from '../../types/api';
import type { TradingSignal } from '../../types/trading';
import { format } from 'date-fns';
import './CombinedChart.css';

interface CombinedChartProps {
  historicalData: PricePoint[];
  predictions: Prediction[];
  commodity: string;
  height?: number;
  signals?: TradingSignal[];
  showSignals?: boolean;
}

const CombinedChart: React.FC<CombinedChartProps> = ({
  historicalData,
  predictions,
  commodity,
  height = 500,
  signals = [],
  showSignals = false,
}) => {
  const chartId = `combined-chart-${commodity}-${Date.now()}`;
  // Find the last historical date
  const lastHistoricalDate = historicalData.length > 0
    ? historicalData[historicalData.length - 1].timestamp
    : null;

  // Transform historical data
  const historicalChartData = historicalData.map((point) => ({
    date: format(new Date(point.timestamp), 'yyyy-MM-dd'),
    historicalPrice: point.price,
    forecastPrice: null,
    confidenceLower: null,
    confidenceUpper: null,
    type: 'historical' as const,
  }));

  // Transform forecast data
  const forecastChartData = predictions.map((pred) => ({
    date: pred.date,
    historicalPrice: null,
    forecastPrice: pred.price,
    confidenceLower: pred.confidence_lower,
    confidenceUpper: pred.confidence_upper,
    type: 'forecast' as const,
  }));

  // Combine data
  const chartData = [...historicalChartData, ...forecastChartData].sort((a, b) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Prepare signal data for scatter plot
  const buySignals = showSignals
    ? signals
        .filter((s) => s.signal === 'buy')
        .map((s) => ({
          date: s.date,
          price: s.price,
          signal: 'buy',
        }))
    : [];

  const sellSignals = showSignals
    ? signals
        .filter((s) => s.signal === 'sell')
        .map((s) => ({
          date: s.date,
          price: s.price,
          signal: 'sell',
        }))
    : [];

  return (
    <div className="combined-chart">
      <h3>{commodity} Historical Prices & Forecast</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => format(new Date(value), 'MMM dd')}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
            domain={['dataMin - 5', 'dataMax + 5']}
          />
          <Tooltip
            labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy')}
            formatter={(value: unknown, name?: string) => {
              const displayName = name || 'Value';
              if (value === null || value === undefined) return [null, displayName];
              const numValue = typeof value === 'number' ? value : 0;
              return [`$${numValue.toFixed(2)}`, displayName];
            }}
          />
          <Legend />
          {lastHistoricalDate && (
            <ReferenceLine
              x={format(new Date(lastHistoricalDate), 'yyyy-MM-dd')}
              stroke="#ef4444"
              strokeDasharray="3 3"
              label={{ value: 'Forecast Start', position: 'top' }}
            />
          )}
          <Line
            type="monotone"
            dataKey="historicalPrice"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Historical Price"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="forecastPrice"
            stroke="#3b82f6"
            strokeWidth={3}
            strokeDasharray="5 5"
            dot={{ fill: '#3b82f6', r: 4 }}
            name="Forecast"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="confidenceLower"
            stroke="#93c5fd"
            strokeWidth={1}
            strokeDasharray="2 2"
            dot={false}
            name="Lower Bound"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="confidenceUpper"
            stroke="#93c5fd"
            strokeWidth={1}
            strokeDasharray="2 2"
            dot={false}
            name="Upper Bound"
            connectNulls={false}
          />
          {showSignals && buySignals.length > 0 && (
            <Scatter
              data={buySignals}
              fill="#10b981"
              shape={(props: { cx?: number; cy?: number }) => (
                <g>
                  <circle cx={props.cx} cy={props.cy} r={6} fill="#10b981" />
                  <text
                    x={props.cx}
                    y={(props.cy || 0) - 10}
                    textAnchor="middle"
                    fontSize="16"
                    fill="#10b981"
                    fontWeight="bold"
                  >
                    ↑
                  </text>
                </g>
              )}
              name="Buy Signal"
            />
          )}
          {showSignals && sellSignals.length > 0 && (
            <Scatter
              data={sellSignals}
              fill="#ef4444"
              shape={(props: { cx?: number; cy?: number }) => (
                <g>
                  <circle cx={props.cx} cy={props.cy} r={6} fill="#ef4444" />
                  <text
                    x={props.cx}
                    y={(props.cy || 0) + 20}
                    textAnchor="middle"
                    fontSize="16"
                    fill="#ef4444"
                    fontWeight="bold"
                  >
                    ↓
                  </text>
                </g>
              )}
              name="Sell Signal"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      {showSignals && signals.length > 0 && (
        <div className="signals-legend">
          <div className="signal-item">
            <span className="signal-indicator buy">↑</span>
            <span>Buy Signal ({signals.filter((s) => s.signal === 'buy').length})</span>
          </div>
          <div className="signal-item">
            <span className="signal-indicator sell">↓</span>
            <span>Sell Signal ({signals.filter((s) => s.signal === 'sell').length})</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default CombinedChart;

