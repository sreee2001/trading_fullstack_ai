/**
 * Layout Component
 * 
 * Main layout wrapper with navigation and header.
 */

import { useState } from 'react';
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">Energy Price Forecasting</h1>
          <button
            className="mobile-menu-toggle"
            onClick={toggleMobileMenu}
            aria-label="Toggle menu"
          >
            <span className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
          <nav className={`nav ${mobileMenuOpen ? 'open' : ''}`}>
            <Link
              to="/"
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Home
            </Link>
            <Link
              to="/forecast"
              className={`nav-link ${isActive('/forecast') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Forecast
            </Link>
            <Link
              to="/models"
              className={`nav-link ${isActive('/models') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Models
            </Link>
            <Link
              to="/backtest"
              className={`nav-link ${isActive('/backtest') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              Backtest
            </Link>
            <div className="mobile-header-actions">
              {state.isAuthenticated ? (
                <button onClick={() => { clearAuth(); closeMobileMenu(); }} className="btn-secondary">
                  Logout
                </button>
              ) : (
                <span className="auth-status">Not Authenticated</span>
              )}
            </div>
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
      {mobileMenuOpen && <div className="mobile-menu-overlay" onClick={closeMobileMenu} />}
      <main className="main-content">{children}</main>
      <footer className="footer">
        <p>&copy; 2025 Energy Price Forecasting System</p>
      </footer>
    </div>
  );
};

export default Layout;

