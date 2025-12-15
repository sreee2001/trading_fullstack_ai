/**
 * Models Page Component
 * 
 * Page for viewing ML model information and performance metrics.
 */

import React, { useState, useEffect } from 'react';
import { modelsService } from '../services/modelsService';
import { useApp } from '../context/AppContext';
import MetricCard from '../components/MetricCard';
import ModelComparisonTable from '../components/ModelComparisonTable';
import type { ModelsListResponse, ModelInfo } from '../types/api';
import './Models.css';

const Models: React.FC = () => {
  const { state } = useApp();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('');

  useEffect(() => {
    if (state.isAuthenticated) {
      fetchModels();
    }
  }, [state.isAuthenticated, selectedCommodity]);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);

    try {
      const response: ModelsListResponse = await modelsService.getAllModels(
        selectedCommodity || undefined
      );
      setModels(response.models);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch models');
    } finally {
      setLoading(false);
    }
  };

  // Calculate aggregate metrics from all models
  const aggregateMetrics = () => {
    if (models.length === 0) return null;

    const metricsWithValues = models.filter((m) => m.metrics.rmse !== undefined);
    if (metricsWithValues.length === 0) return null;

    const avgRmse =
      metricsWithValues.reduce((sum, m) => sum + (m.metrics.rmse ?? 0), 0) /
      metricsWithValues.length;

    const avgMae =
      metricsWithValues.reduce((sum, m) => sum + (m.metrics.mae ?? 0), 0) /
      metricsWithValues.length;

    const avgDirectionalAccuracy =
      models
        .filter((m) => m.metrics.directional_accuracy !== undefined)
        .reduce(
          (sum, m) => sum + (m.metrics.directional_accuracy ?? 0),
          0
        ) / models.filter((m) => m.metrics.directional_accuracy !== undefined).length;

    const avgSharpeRatio =
      models
        .filter((m) => m.metrics.sharpe_ratio !== undefined)
        .reduce((sum, m) => sum + (m.metrics.sharpe_ratio ?? 0), 0) /
      models.filter((m) => m.metrics.sharpe_ratio !== undefined).length;

    return {
      avgRmse,
      avgMae,
      avgDirectionalAccuracy,
      avgSharpeRatio,
    };
  };

  const aggregate = aggregateMetrics();

  return (
    <div className="models-page">
      <h1>ML Models</h1>

      <div className="models-controls">
        <div className="control-group">
          <label htmlFor="commodityFilter">Filter by Commodity:</label>
          <select
            id="commodityFilter"
            value={selectedCommodity}
            onChange={(e) => setSelectedCommodity(e.target.value)}
          >
            <option value="">All Commodities</option>
            <option value="WTI">WTI</option>
            <option value="BRENT">BRENT</option>
            <option value="NG">Natural Gas</option>
          </select>
        </div>
        <button onClick={fetchModels} disabled={loading} className="btn-primary">
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {!state.isAuthenticated && (
        <div className="warning-message">
          Please configure your API key in the environment variables to use this feature.
        </div>
      )}

      {loading && <div className="loading-message">Loading models...</div>}

      {!loading && models.length > 0 && (
        <>
          {aggregate && (
            <div className="metrics-grid">
              <MetricCard
                title="Average RMSE"
                value={aggregate.avgRmse}
                color="blue"
              />
              <MetricCard
                title="Average MAE"
                value={aggregate.avgMae}
                color="green"
              />
              <MetricCard
                title="Average Directional Accuracy"
                value={`${(aggregate.avgDirectionalAccuracy * 100).toFixed(1)}%`}
                color="purple"
              />
              <MetricCard
                title="Average Sharpe Ratio"
                value={aggregate.avgSharpeRatio}
                color="yellow"
              />
            </div>
          )}

          <div className="models-section">
            <ModelComparisonTable models={models} />
          </div>
        </>
      )}

      {!loading && models.length === 0 && state.isAuthenticated && (
        <div className="empty-message">No models found.</div>
      )}
    </div>
  );
};

export default Models;

