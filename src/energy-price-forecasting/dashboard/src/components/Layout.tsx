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
  const { state, setApiKey, clearAuth } = useApp();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);
  const [apiKeyValue, setApiKeyValue] = useState('');

  const isActive = (path: string) => location.pathname === path;

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  const handleApiKeySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (apiKeyValue.trim()) {
      setApiKey(apiKeyValue.trim());
      setApiKeyValue('');
      setShowApiKeyInput(false);
    }
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
                <div className="auth-section">
                  <input
                    type="text"
                    placeholder="Enter API key (epf_...)"
                    value={apiKeyValue}
                    onChange={(e) => setApiKeyValue(e.target.value)}
                    className="api-key-input"
                  />
                  <button 
                    onClick={() => {
                      if (apiKeyValue.trim()) {
                        setApiKey(apiKeyValue.trim());
                        setApiKeyValue('');
                        closeMobileMenu();
                      }
                    }}
                    className="btn-primary"
                  >
                    Save API Key
                  </button>
                </div>
              )}
            </div>
          </nav>
          <div className="header-actions">
            {state.isAuthenticated ? (
              <button onClick={clearAuth} className="btn-secondary">
                Logout
              </button>
            ) : (
              <div className="auth-section">
                {!showApiKeyInput ? (
                  <button 
                    onClick={() => setShowApiKeyInput(true)} 
                    className="btn-secondary"
                  >
                    Enter API Key
                  </button>
                ) : (
                  <form onSubmit={handleApiKeySubmit} className="api-key-form">
                    <input
                      type="text"
                      placeholder="Enter API key (epf_...)"
                      value={apiKeyValue}
                      onChange={(e) => setApiKeyValue(e.target.value)}
                      className="api-key-input"
                      autoFocus
                    />
                    <button type="submit" className="btn-primary">Save</button>
                    <button 
                      type="button" 
                      onClick={() => {
                        setShowApiKeyInput(false);
                        setApiKeyValue('');
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </form>
                )}
              </div>
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

