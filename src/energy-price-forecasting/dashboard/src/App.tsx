/**
 * Main App Component
 * 
 * Sets up routing and application context provider.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Forecast from './pages/Forecast';
import Models from './pages/Models';
import Backtest from './pages/Backtest';
import './App.css';

function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/models" element={<Models />} />
            <Route path="/backtest" element={<Backtest />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
