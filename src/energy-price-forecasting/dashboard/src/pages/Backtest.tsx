/**
 * Backtest Page Component
 * 
 * Page for running backtests on forecasting models.
 */

import React, { useState, useEffect } from 'react';
import { backtestService } from '../services/backtestService';
import { modelsService } from '../services/modelsService';
import { useApp } from '../context/AppContext';
import MetricCard from '../components/MetricCard';
import EquityCurveChart from '../components/charts/EquityCurveChart';
import TradeHistoryTable from '../components/TradeHistoryTable';
import type { BacktestRequest, BacktestResponse } from '../types/api';
import type { ModelInfo } from '../types/api';
import './Backtest.css';

// Helper function to generate dates for equity curve
const generateEquityDates = (startDate: string, endDate: string, count: number): string[] => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const dates: string[] = [];
  const step = (end.getTime() - start.getTime()) / (count - 1);
  
  for (let i = 0; i < count; i++) {
    const date = new Date(start.getTime() + step * i);
    dates.push(date.toISOString().split('T')[0]);
  }
  
  return dates;
};

const Backtest: React.FC = () => {
  const { state } = useApp();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('');
  const [startDate, setStartDate] = useState<string>(
    new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [initialCapital, setInitialCapital] = useState<number>(100000);
  const [commission, setCommission] = useState<number>(0.001);
  const [slippage, setSlippage] = useState<number>(0.0005);
  const [strategy, setStrategy] = useState<string>('threshold');
  const [threshold, setThreshold] = useState<number>(0.02);
  const [loading, setLoading] = useState<boolean>(false);
  const [backtestResult, setBacktestResult] = useState<BacktestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (state.isAuthenticated) {
      fetchModels();
    }
  }, [state.isAuthenticated]);

  const fetchModels = async () => {
    try {
      const response = await modelsService.getAllModels();
      setModels(response.models);
      if (response.models.length > 0) {
        setSelectedModelId(response.models[0].model_id);
      }
    } catch (err) {
      console.error('Failed to fetch models:', err);
    }
  };

  const handleRunBacktest = async () => {
    if (!state.isAuthenticated) {
      setError('Please authenticate with an API key first');
      return;
    }

    if (!selectedModelId) {
      setError('Please select a model');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const request: BacktestRequest = {
        model_id: selectedModelId,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        commission: commission,
        slippage: slippage,
        strategy_params: {
          strategy_name: strategy,
          threshold: threshold,
        },
      };

      const result = await backtestService.runBacktest(request);
      setBacktestResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run backtest');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="backtest-page">
      <h1>Backtest</h1>

      <div className="backtest-controls">
        <div className="control-group">
          <label htmlFor="model">Model:</label>
          <select
            id="model"
            value={selectedModelId}
            onChange={(e) => setSelectedModelId(e.target.value)}
          >
            <option value="">Select a model</option>
            {models.map((model) => (
              <option key={model.model_id} value={model.model_id}>
                {model.commodity} - {model.model_type} ({model.stage})
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="startDate">Start Date:</label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div className="control-group">
          <label htmlFor="endDate">End Date:</label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>

        <div className="control-group">
          <label htmlFor="initialCapital">Initial Capital:</label>
          <input
            id="initialCapital"
            type="number"
            min="1000"
            step="1000"
            value={initialCapital}
            onChange={(e) => setInitialCapital(parseFloat(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label htmlFor="commission">Commission:</label>
          <input
            id="commission"
            type="number"
            min="0"
            max="0.1"
            step="0.0001"
            value={commission}
            onChange={(e) => setCommission(parseFloat(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label htmlFor="slippage">Slippage:</label>
          <input
            id="slippage"
            type="number"
            min="0"
            max="0.1"
            step="0.0001"
            value={slippage}
            onChange={(e) => setSlippage(parseFloat(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label htmlFor="strategy">Strategy:</label>
          <select
            id="strategy"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
          >
            <option value="threshold">Threshold</option>
            <option value="momentum">Momentum</option>
            <option value="mean_reversion">Mean Reversion</option>
          </select>
        </div>

        {strategy === 'threshold' && (
          <div className="control-group">
            <label htmlFor="threshold">Threshold:</label>
            <input
              id="threshold"
              type="number"
              min="0"
              max="0.1"
              step="0.001"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
            />
          </div>
        )}

        <button
          onClick={handleRunBacktest}
          disabled={loading || !selectedModelId || !state.isAuthenticated}
          className="btn-primary"
        >
          {loading ? 'Running Backtest...' : 'Run Backtest'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {!state.isAuthenticated && (
        <div className="warning-message">
          Please configure your API key in the environment variables to use this feature.
        </div>
      )}

      {backtestResult && (
        <div className="backtest-results">
          <h2>Backtest Results</h2>

          <div className="metrics-grid">
            <MetricCard
              title="Total Return"
              value={`${((backtestResult.metrics.total_return || 0) * 100).toFixed(2)}%`}
              color={backtestResult.metrics.total_return !== undefined && backtestResult.metrics.total_return >= 0 ? 'green' : 'red'}
            />
            <MetricCard
              title="Sharpe Ratio"
              value={backtestResult.metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
              color="blue"
            />
            <MetricCard
              title="Sortino Ratio"
              value={backtestResult.metrics.sortino_ratio?.toFixed(2) || 'N/A'}
              color="purple"
            />
            <MetricCard
              title="Max Drawdown"
              value={`${((backtestResult.metrics.max_drawdown || 0) * 100).toFixed(2)}%`}
              color="red"
            />
            <MetricCard
              title="Win Rate"
              value={`${((backtestResult.metrics.win_rate || 0) * 100).toFixed(1)}%`}
              color="yellow"
            />
            <MetricCard
              title="Total Trades"
              value={backtestResult.num_trades}
              color="gray"
            />
          </div>

          {backtestResult.equity_curve && backtestResult.equity_curve.length > 0 && (
            <div className="equity-section">
              <EquityCurveChart
                dates={generateEquityDates(backtestResult.start_date, backtestResult.end_date, backtestResult.equity_curve.length)}
                values={backtestResult.equity_curve}
                initialCapital={backtestResult.metrics.initial_capital || 100000}
                finalCapital={backtestResult.metrics.final_capital || 100000}
              />
            </div>
          )}

          {backtestResult.trades && backtestResult.trades.length > 0 && (
            <div className="trades-section">
              <TradeHistoryTable 
                trades={backtestResult.trades}
                startDate={backtestResult.start_date}
                endDate={backtestResult.end_date}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Backtest;

