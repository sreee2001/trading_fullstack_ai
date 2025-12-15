/**
 * Home Page Component
 * 
 * Landing page with overview and navigation.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      <section className="hero">
        <h1>Energy Price Forecasting System</h1>
        <p className="subtitle">
          Advanced ML-powered forecasting for WTI, BRENT, and Natural Gas commodities
        </p>
      </section>

      <section className="features">
        <div className="feature-card">
          <h2>📈 Forecast</h2>
          <p>Generate price forecasts for energy commodities using advanced ML models</p>
          <Link to="/forecast" className="feature-link">
            View Forecasts →
          </Link>
        </div>

        <div className="feature-card">
          <h2>🤖 Models</h2>
          <p>Explore and compare ML model performance metrics and metadata</p>
          <Link to="/models" className="feature-link">
            View Models →
          </Link>
        </div>

        <div className="feature-card">
          <h2>📊 Backtest</h2>
          <p>Run backtests on forecasting models with custom trading strategies</p>
          <Link to="/backtest" className="feature-link">
            Run Backtest →
          </Link>
        </div>
      </section>

      <section className="info">
        <h2>About</h2>
        <p>
          This system provides comprehensive energy commodity price forecasting using
          multiple machine learning models including ARIMA, Prophet, and LSTM neural networks.
        </p>
        <p>
          Features include multi-horizon forecasting (1, 7, 30 days), comprehensive backtesting,
          and real-time model performance monitoring.
        </p>
      </section>
    </div>
  );
};

export default Home;

