/**
 * Historical Price Chart Component
 * 
 * Displays historical price data as a time series line chart.
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
} from 'recharts';
import type { PricePoint } from '../../types/api';
import { format } from 'date-fns';
import './HistoricalPriceChart.css';

interface HistoricalPriceChartProps {
  data: PricePoint[];
  commodity: string;
  height?: number;
}

const HistoricalPriceChart: React.FC<HistoricalPriceChartProps> = ({
  data,
  commodity,
  height = 400,
}) => {
  // Transform data for Recharts
  const chartData = data.map((point) => ({
    date: format(new Date(point.timestamp), 'yyyy-MM-dd'),
    price: point.price,
    volume: point.volume || 0,
  }));

  return (
    <div className="historical-price-chart">
      <h3>{commodity} Historical Prices</h3>
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
            formatter={(value: unknown) => {
              const numValue = typeof value === 'number' ? value : 0;
              return [`$${numValue.toFixed(2)}`, 'Price'];
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Price"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HistoricalPriceChart;

