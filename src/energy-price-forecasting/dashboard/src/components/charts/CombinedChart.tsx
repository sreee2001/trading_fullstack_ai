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
} from 'recharts';
import type { PricePoint, Prediction } from '../../types/api';
import { format } from 'date-fns';
import './CombinedChart.css';

interface CombinedChartProps {
  historicalData: PricePoint[];
  predictions: Prediction[];
  commodity: string;
  height?: number;
}

const CombinedChart: React.FC<CombinedChartProps> = ({
  historicalData,
  predictions,
  commodity,
  height = 500,
}) => {
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
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CombinedChart;

