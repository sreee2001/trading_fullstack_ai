/**
 * Forecast Page Component
 * 
 * Page for generating and viewing price forecasts.
 */

import React, { useState } from 'react';
import ForecastChart from '../components/charts/ForecastChart';
import CombinedChart from '../components/charts/CombinedChart';
import HistoricalPriceChart from '../components/charts/HistoricalPriceChart';
import ComparisonChart from '../components/charts/ComparisonChart';
import { forecastService } from '../services/forecastService';
import { historicalService } from '../services/historicalService';
import { generateSignals } from '../services/signalService';
import { exportChartAsPNG, exportDataAsCSV } from '../utils/exportUtils';
import { useApp } from '../context/AppContext';
import type { ForecastResponse, HistoricalDataResponse } from '../types/api';
import type { TradingSignal } from '../types/trading';
import './Forecast.css';

const Forecast: React.FC = () => {
  const { state } = useApp();
  const [commodity, setCommodity] = useState<'WTI' | 'BRENT' | 'NG'>('WTI');
  const [horizon, setHorizon] = useState<number>(7);
  const [startDate, setStartDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalDataResponse | null>(null);
  const [actualData, setActualData] = useState<HistoricalDataResponse | null>(null);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [showSignals, setShowSignals] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showCombined, setShowCombined] = useState<boolean>(false);
  const [showComparison, setShowComparison] = useState<boolean>(false);

  const handleGenerateForecast = async () => {
    if (!state.isAuthenticated) {
      setError('Please authenticate with an API key first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get historical data for the past 30 days
      const endDate = new Date(startDate);
      const historicalStartDate = new Date(endDate);
      historicalStartDate.setDate(historicalStartDate.getDate() - 30);

      // Calculate end date for actual data (startDate + horizon days)
      const actualEndDate = new Date(startDate);
      actualEndDate.setDate(actualEndDate.getDate() + horizon);

      const [forecastResponse, historicalResponse, actualResponse] = await Promise.all([
        forecastService.generateForecast({
          commodity,
          horizon,
          start_date: startDate,
        }),
        historicalService.getHistoricalData({
          commodity,
          start_date: historicalStartDate.toISOString().split('T')[0],
          end_date: startDate,
          limit: 1000,
        }),
        historicalService.getHistoricalData({
          commodity,
          start_date: startDate,
          end_date: actualEndDate.toISOString().split('T')[0],
          limit: 1000,
        }),
      ]);

      setForecast(forecastResponse);
      setHistoricalData(historicalResponse);
      setActualData(actualResponse);

      // Generate trading signals
      const generatedSignals = generateSignals(
        forecastResponse.predictions,
        [...historicalResponse.data, ...actualResponse.data],
        'threshold',
        0.02
      );
      setSignals(generatedSignals);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forecast-page">
      <h1>Price Forecast</h1>

      <div className="forecast-controls">
        <div className="control-group">
          <label htmlFor="commodity">Commodity:</label>
          <select
            id="commodity"
            value={commodity}
            onChange={(e) => setCommodity(e.target.value as 'WTI' | 'BRENT' | 'NG')}
          >
            <option value="WTI">WTI</option>
            <option value="BRENT">BRENT</option>
            <option value="NG">Natural Gas</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="horizon">Forecast Horizon (days):</label>
          <input
            id="horizon"
            type="number"
            min="1"
            max="30"
            value={horizon}
            onChange={(e) => setHorizon(parseInt(e.target.value, 10))}
          />
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

        <button
          onClick={handleGenerateForecast}
          disabled={loading || !state.isAuthenticated}
          className="btn-primary"
        >
          {loading ? 'Generating...' : 'Generate Forecast'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {!state.isAuthenticated && (
        <div className="warning-message">
          Please configure your API key in the environment variables to use this feature.
        </div>
      )}

      {forecast && (
        <div className="forecast-results">
          <div className="chart-toggle">
            <button
              onClick={() => {
                setShowCombined(!showCombined);
                setShowComparison(false);
              }}
              className="btn-secondary"
            >
              {showCombined ? 'Show Forecast Only' : 'Show Combined View'}
            </button>
            {actualData && actualData.data.length > 0 && (
              <button
                onClick={() => {
                  setShowComparison(!showComparison);
                  setShowCombined(false);
                }}
                className="btn-secondary"
              >
                {showComparison ? 'Show Forecast Only' : 'Show Forecast vs Actual'}
              </button>
            )}
            {signals.length > 0 && (
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={showSignals}
                  onChange={(e) => setShowSignals(e.target.checked)}
                />
                Show Trading Signals ({signals.length})
              </label>
            )}
          </div>

          {showComparison && actualData ? (
            <ComparisonChart
              predictions={forecast.predictions}
              actualPrices={actualData.data}
              commodity={forecast.commodity}
            />
          ) : showCombined && historicalData ? (
            <div id="combined-chart-container">
              <CombinedChart
                historicalData={historicalData.data}
                predictions={forecast.predictions}
                commodity={forecast.commodity}
                signals={signals}
                showSignals={showSignals}
              />
            </div>
          ) : (
            <ForecastChart
              predictions={forecast.predictions}
              commodity={forecast.commodity}
            />
          )}

          {historicalData && !showCombined && !showComparison && (
            <div className="historical-section">
              <HistoricalPriceChart
                data={historicalData.data}
                commodity={historicalData.commodity}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Forecast;

