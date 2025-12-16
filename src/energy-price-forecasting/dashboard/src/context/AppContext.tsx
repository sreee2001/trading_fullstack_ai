/**
 * Application Context for Global State Management
 * 
 * Provides global state management using React Context API.
 * Manages application-wide state such as API key, user preferences, etc.
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

// Application State Interface
interface AppState {
  apiKey: string | null;
  isAuthenticated: boolean;
  theme: 'light' | 'dark';
  selectedCommodity: 'WTI' | 'BRENT' | 'NG' | null;
}

// Context Interface
interface AppContextType {
  state: AppState;
  setApiKey: (key: string | null) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setSelectedCommodity: (commodity: 'WTI' | 'BRENT' | 'NG' | null) => void;
  clearAuth: () => void;
}

// Get API key from environment variable or localStorage
const getInitialApiKey = (): string | null => {
  // Check environment variable first (Vite uses import.meta.env)
  const envApiKey = import.meta.env.VITE_API_KEY;
  if (envApiKey && envApiKey.trim() && envApiKey !== 'your_api_key_here') {
    // Store in localStorage for consistency
    localStorage.setItem('apiKey', envApiKey.trim());
    return envApiKey.trim();
  }
  // Fallback to localStorage
  return localStorage.getItem('apiKey');
};

// Initial State
const initialState: AppState = {
  apiKey: getInitialApiKey(),
  isAuthenticated: !!getInitialApiKey(),
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  selectedCommodity: null,
};

// Create Context
const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider Component
interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, setState] = useState<AppState>(initialState);

  // Set API Key
  const setApiKey = useCallback((key: string | null) => {
    if (key) {
      localStorage.setItem('apiKey', key);
      setState((prev) => ({
        ...prev,
        apiKey: key,
        isAuthenticated: true,
      }));
    } else {
      localStorage.removeItem('apiKey');
      setState((prev) => ({
        ...prev,
        apiKey: null,
        isAuthenticated: false,
      }));
    }
  }, []);

  // Set Theme
  const setTheme = useCallback((theme: 'light' | 'dark') => {
    localStorage.setItem('theme', theme);
    setState((prev) => ({ ...prev, theme }));
  }, []);

  // Set Selected Commodity
  const setSelectedCommodity = useCallback((commodity: 'WTI' | 'BRENT' | 'NG' | null) => {
    setState((prev) => ({ ...prev, selectedCommodity: commodity }));
  }, []);

  // Clear Authentication
  const clearAuth = useCallback(() => {
    setApiKey(null);
  }, [setApiKey]);

  const value: AppContextType = {
    state,
    setApiKey,
    setTheme,
    setSelectedCommodity,
    clearAuth,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Custom Hook
export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

