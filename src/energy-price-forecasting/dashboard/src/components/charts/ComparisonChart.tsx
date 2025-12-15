/**
 * Comparison Chart Component
 * 
 * Displays forecast predictions vs actual prices for accuracy comparison.
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
import type { Prediction, PricePoint } from '../../types/api';
import { format } from 'date-fns';
import './ComparisonChart.css';

interface ComparisonChartProps {
  predictions: Prediction[];
  actualPrices: PricePoint[];
  commodity: string;
  height?: number;
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({
  predictions,
  actualPrices,
  commodity,
  height = 400,
}) => {
  // Create a map of actual prices by date for quick lookup
  const actualPriceMap = new Map<string, number>();
  actualPrices.forEach((point) => {
    const date = format(new Date(point.timestamp), 'yyyy-MM-dd');
    actualPriceMap.set(date, point.price);
  });

  // Combine predictions with actual prices where available
  const chartData = predictions.map((pred) => {
    const actualPrice = actualPriceMap.get(pred.date);
    return {
      date: pred.date,
      predicted: pred.price,
      actual: actualPrice ?? null,
      confidenceLower: pred.confidence_lower,
      confidenceUpper: pred.confidence_upper,
    };
  });

  // Calculate accuracy metrics
  const metrics = React.useMemo(() => {
    const validPairs = chartData.filter((d) => d.actual !== null);
    if (validPairs.length === 0) return null;

    let sumSquaredError = 0;
    let sumAbsoluteError = 0;
    let correctDirection = 0;
    let totalPairs = 0;

    for (let i = 1; i < validPairs.length; i++) {
      const prev = validPairs[i - 1];
      const curr = validPairs[i];

      if (prev.actual !== null && curr.actual !== null && curr.predicted !== null) {
        const actualChange = curr.actual - prev.actual;
        const predictedChange = curr.predicted - prev.predicted;

        // Same direction
        if (
          (actualChange > 0 && predictedChange > 0) ||
          (actualChange < 0 && predictedChange < 0) ||
          (actualChange === 0 && predictedChange === 0)
        ) {
          correctDirection++;
        }

        const error = curr.predicted - curr.actual;
        sumSquaredError += error * error;
        sumAbsoluteError += Math.abs(error);
        totalPairs++;
      }
    }

    const rmse = Math.sqrt(sumSquaredError / totalPairs);
    const mae = sumAbsoluteError / totalPairs;
    const directionalAccuracy = correctDirection / (validPairs.length - 1);

    return {
      rmse,
      mae,
      directionalAccuracy,
      dataPoints: validPairs.length,
    };
  }, [chartData]);

  return (
    <div className="comparison-chart">
      <h3>{commodity} Forecast vs Actual</h3>
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
              if (value === null || value === undefined) return [null, name];
              const numValue = typeof value === 'number' ? value : 0;
              return [`$${numValue.toFixed(2)}`, name];
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ fill: '#3b82f6', r: 3 }}
            name="Predicted"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', r: 3 }}
            name="Actual"
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
      {metrics && (
        <div className="accuracy-metrics">
          <h4>Accuracy Metrics</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <span className="metric-label">RMSE:</span>
              <span className="metric-value">{metrics.rmse.toFixed(4)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">MAE:</span>
              <span className="metric-value">{metrics.mae.toFixed(4)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Directional Accuracy:</span>
              <span className="metric-value">
                {(metrics.directionalAccuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Data Points:</span>
              <span className="metric-value">{metrics.dataPoints}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonChart;

