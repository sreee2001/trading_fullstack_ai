/**
 * Forecast Chart Component
 * 
 * Displays forecast predictions with confidence intervals.
 */

import React from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import type { Prediction } from '../../types/api';
import { format } from 'date-fns';
import './ForecastChart.css';

interface ForecastChartProps {
  predictions: Prediction[];
  commodity: string;
  height?: number;
}

const ForecastChart: React.FC<ForecastChartProps> = ({
  predictions,
  commodity,
  height = 400,
}) => {
  const chartId = `forecast-chart-${commodity}-${Date.now()}`;
  // Transform data for Recharts
  const chartData = predictions.map((pred) => ({
    date: pred.date,
    price: pred.price,
    confidenceLower: pred.confidence_lower,
    confidenceUpper: pred.confidence_upper,
  }));

  return (
    <div className="forecast-chart">
      <h3>{commodity} Price Forecast</h3>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
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
              const numValue = typeof value === 'number' ? value : 0;
              const displayName = name || 'Value';
              if (name === 'price') return [`$${numValue.toFixed(2)}`, 'Forecast'];
              if (name === 'confidenceLower') return [`$${numValue.toFixed(2)}`, 'Lower Bound'];
              if (name === 'confidenceUpper') return [`$${numValue.toFixed(2)}`, 'Upper Bound'];
              return [`$${numValue.toFixed(2)}`, displayName];
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="confidenceUpper"
            stroke="none"
            fill="none"
            name="Confidence Interval"
          />
          <Area
            type="monotone"
            dataKey="confidenceLower"
            stroke="none"
            fill="url(#confidenceGradient)"
            name="Confidence Interval"
          />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ fill: '#3b82f6', r: 4 }}
            name="Forecast"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForecastChart;

