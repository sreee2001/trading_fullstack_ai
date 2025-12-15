/**
 * Layout Component
 * 
 * Main layout wrapper with navigation and header.
 */

import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const { state, clearAuth } = useApp();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">Energy Price Forecasting</h1>
          <nav className="nav">
            <Link
              to="/"
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
            >
              Home
            </Link>
            <Link
              to="/forecast"
              className={`nav-link ${isActive('/forecast') ? 'active' : ''}`}
            >
              Forecast
            </Link>
            <Link
              to="/models"
              className={`nav-link ${isActive('/models') ? 'active' : ''}`}
            >
              Models
            </Link>
            <Link
              to="/backtest"
              className={`nav-link ${isActive('/backtest') ? 'active' : ''}`}
            >
              Backtest
            </Link>
          </nav>
          <div className="header-actions">
            {state.isAuthenticated ? (
              <button onClick={clearAuth} className="btn-secondary">
                Logout
              </button>
            ) : (
              <span className="auth-status">Not Authenticated</span>
            )}
          </div>
        </div>
      </header>
      <main className="main-content">{children}</main>
      <footer className="footer">
        <p>&copy; 2025 Energy Price Forecasting System</p>
      </footer>
    </div>
  );
};

export default Layout;

