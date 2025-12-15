/**
 * Forecast Page Component
 * 
 * Page for generating and viewing price forecasts.
 */

import React, { useState } from 'react';
import ForecastChart from '../components/charts/ForecastChart';
import CombinedChart from '../components/charts/CombinedChart';
import HistoricalPriceChart from '../components/charts/HistoricalPriceChart';
import { forecastService } from '../services/forecastService';
import { historicalService } from '../services/historicalService';
import { useApp } from '../context/AppContext';
import type { ForecastRequest, ForecastResponse, HistoricalDataResponse } from '../types/api';
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
  const [error, setError] = useState<string | null>(null);
  const [showCombined, setShowCombined] = useState<boolean>(false);

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

      const [forecastResponse, historicalResponse] = await Promise.all([
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
      ]);

      setForecast(forecastResponse);
      setHistoricalData(historicalResponse);
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
              onClick={() => setShowCombined(!showCombined)}
              className="btn-secondary"
            >
              {showCombined ? 'Show Forecast Only' : 'Show Combined View'}
            </button>
          </div>

          {showCombined && historicalData ? (
            <CombinedChart
              historicalData={historicalData.data}
              predictions={forecast.predictions}
              commodity={forecast.commodity}
            />
          ) : (
            <ForecastChart
              predictions={forecast.predictions}
              commodity={forecast.commodity}
            />
          )}

          {historicalData && !showCombined && (
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

