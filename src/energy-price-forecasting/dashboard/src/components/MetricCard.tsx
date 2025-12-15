/**
 * Metric Card Component
 * 
 * Reusable component for displaying metrics in a card format.
 */

import React from 'react';
import './MetricCard.css';

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'gray';
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit = '',
  color = 'blue',
  trend,
  trendValue,
}) => {
  const formatValue = (val: number | string): string => {
    if (typeof val === 'number') {
      // Format numbers with appropriate precision
      if (val >= 1000) {
        return val.toLocaleString('en-US', { maximumFractionDigits: 2 });
      }
      if (val < 1 && val > 0) {
        return val.toFixed(4);
      }
      return val.toFixed(2);
    }
    return val;
  };

  const getColorClass = () => {
    const colorMap = {
      blue: 'metric-blue',
      green: 'metric-green',
      red: 'metric-red',
      yellow: 'metric-yellow',
      purple: 'metric-purple',
      gray: 'metric-gray',
    };
    return colorMap[color];
  };

  const getTrendIcon = () => {
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '';
  };

  return (
    <div className={`metric-card ${getColorClass()}`}>
      <div className="metric-header">
        <h4 className="metric-title">{title}</h4>
        {trend && (
          <span className={`metric-trend trend-${trend}`}>
            {getTrendIcon()} {trendValue}
          </span>
        )}
      </div>
      <div className="metric-value">
        {formatValue(value)}
        {unit && <span className="metric-unit">{unit}</span>}
      </div>
    </div>
  );
};

export default MetricCard;

