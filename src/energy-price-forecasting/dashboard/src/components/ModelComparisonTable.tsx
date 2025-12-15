/**
 * Model Comparison Table Component
 * 
 * Displays a sortable table comparing model performance metrics.
 */

import React, { useState, useMemo } from 'react';
import type { ModelInfo } from '../types/api';
import './ModelComparisonTable.css';

interface ModelComparisonTableProps {
  models: ModelInfo[];
}

type SortField = 'model_type' | 'rmse' | 'mae' | 'sharpe_ratio' | 'directional_accuracy';
type SortDirection = 'asc' | 'desc';

const ModelComparisonTable: React.FC<ModelComparisonTableProps> = ({ models }) => {
  const [sortField, setSortField] = useState<SortField>('rmse');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const sortedModels = useMemo(() => {
    const sorted = [...models].sort((a, b) => {
      let aValue: number | string = 0;
      let bValue: number | string = 0;

      switch (sortField) {
        case 'model_type':
          aValue = a.model_type;
          bValue = b.model_type;
          break;
        case 'rmse':
          aValue = a.metrics.rmse ?? Infinity;
          bValue = b.metrics.rmse ?? Infinity;
          break;
        case 'mae':
          aValue = a.metrics.mae ?? Infinity;
          bValue = b.metrics.mae ?? Infinity;
          break;
        case 'sharpe_ratio':
          aValue = a.metrics.sharpe_ratio ?? -Infinity;
          bValue = b.metrics.sharpe_ratio ?? -Infinity;
          break;
        case 'directional_accuracy':
          aValue = a.metrics.directional_accuracy ?? 0;
          bValue = b.metrics.directional_accuracy ?? 0;
          break;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc'
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });

    return sorted;
  }, [models, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '↕';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  // Find best model (lowest RMSE)
  const bestModelId = useMemo(() => {
    const modelWithRmse = models.filter((m) => m.metrics.rmse !== undefined);
    if (modelWithRmse.length === 0) return null;
    return modelWithRmse.reduce((best, current) =>
      (current.metrics.rmse ?? Infinity) < (best.metrics.rmse ?? Infinity) ? current : best
    ).model_id;
  }, [models]);

  return (
    <div className="model-comparison-table">
      <h3>Model Comparison</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th onClick={() => handleSort('model_type')} className="sortable">
                Model Type {getSortIcon('model_type')}
              </th>
              <th onClick={() => handleSort('rmse')} className="sortable">
                RMSE {getSortIcon('rmse')}
              </th>
              <th onClick={() => handleSort('mae')} className="sortable">
                MAE {getSortIcon('mae')}
              </th>
              <th onClick={() => handleSort('directional_accuracy')} className="sortable">
                Directional Accuracy {getSortIcon('directional_accuracy')}
              </th>
              <th onClick={() => handleSort('sharpe_ratio')} className="sortable">
                Sharpe Ratio {getSortIcon('sharpe_ratio')}
              </th>
              <th>R²</th>
              <th>Stage</th>
            </tr>
          </thead>
          <tbody>
            {sortedModels.map((model) => (
              <tr
                key={model.model_id}
                className={model.model_id === bestModelId ? 'best-model' : ''}
              >
                <td>
                  <strong>{model.model_type}</strong>
                  <div className="model-meta">
                    {model.commodity} v{model.version}
                  </div>
                </td>
                <td>{model.metrics.rmse?.toFixed(4) ?? 'N/A'}</td>
                <td>{model.metrics.mae?.toFixed(4) ?? 'N/A'}</td>
                <td>
                  {model.metrics.directional_accuracy
                    ? `${(model.metrics.directional_accuracy * 100).toFixed(1)}%`
                    : 'N/A'}
                </td>
                <td>{model.metrics.sharpe_ratio?.toFixed(2) ?? 'N/A'}</td>
                <td>{model.metrics.r_squared?.toFixed(3) ?? 'N/A'}</td>
                <td>
                  <span className={`stage-badge stage-${model.stage.toLowerCase()}`}>
                    {model.stage}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {bestModelId && (
        <div className="table-footer">
          <span className="best-model-indicator">★ Best Model (Lowest RMSE)</span>
        </div>
      )}
    </div>
  );
};

export default ModelComparisonTable;

