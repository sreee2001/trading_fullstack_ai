/**
 * Equity Curve Chart Component
 * 
 * Displays the equity curve over time from a backtest.
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
import { format } from 'date-fns';
import './EquityCurveChart.css';

interface EquityCurveChartProps {
  dates: string[];
  values: number[];
  initialCapital: number;
  finalCapital: number;
  height?: number;
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({
  dates,
  values,
  initialCapital,
  finalCapital,
  height = 400,
}) => {
  const chartData = dates.map((date, index) => ({
    date,
    equity: values[index],
  }));

  const totalReturn = ((finalCapital - initialCapital) / initialCapital) * 100;

  return (
    <div className="equity-curve-chart">
      <h3>Equity Curve</h3>
      <div className="equity-summary">
        <div className="summary-item">
          <span className="summary-label">Initial Capital:</span>
          <span className="summary-value">${initialCapital.toLocaleString()}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Final Capital:</span>
          <span className="summary-value">${finalCapital.toLocaleString()}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Total Return:</span>
          <span className={`summary-value ${totalReturn >= 0 ? 'positive' : 'negative'}`}>
            {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
          </span>
        </div>
      </div>
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
            label={{ value: 'Capital ($)', angle: -90, position: 'insideLeft' }}
            domain={['dataMin - 1000', 'dataMax + 1000']}
          />
          <Tooltip
            labelFormatter={(value) => format(new Date(value), 'MMM dd, yyyy')}
            formatter={(value: unknown) => {
              const numValue = typeof value === 'number' ? value : 0;
              return [`$${numValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Equity'];
            }}
          />
          <Legend />
          <ReferenceLine
            y={initialCapital}
            stroke="#64748b"
            strokeDasharray="3 3"
            label={{ value: 'Initial Capital', position: 'right' }}
          />
          <Line
            type="monotone"
            dataKey="equity"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Equity"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityCurveChart;

