/**
 * WebSocket Hook for Real-time Forecast Updates
 * 
 * Provides a React hook for connecting to the WebSocket endpoint
 * and receiving real-time forecast updates.
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: 'connection' | 'forecast' | 'subscription' | 'error' | 'pong';
  status?: string;
  message?: string;
  commodity?: string;
  horizon?: number;
  forecast_date?: string;
  predictions?: Array<{
    date: string;
    price: number;
    confidence_lower: number;
    confidence_upper: number;
  }>;
  model_name?: string;
  model_version?: string;
  timestamp?: string;
}

export interface UseWebSocketOptions {
  commodity?: 'WTI' | 'BRENT' | 'NG';
  horizon?: number;
  autoConnect?: boolean;
  reconnectInterval?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  subscribe: (commodity: string, horizon: number) => void;
  requestForecast: (commodity: string, horizon: number) => void;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WS_BASE_URL = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    commodity = 'WTI',
    horizon = 7,
    autoConnect = false,
    reconnectInterval = 5000,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Event | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    shouldReconnectRef.current = true;

    try {
      const wsUrl = `${WS_BASE_URL}/api/v1/ws/forecast?commodity=${commodity}&horizon=${horizon}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        setError(event);
        onError?.(event);
      };

      ws.onclose = () => {
        setIsConnected(false);
        onDisconnect?.();

        // Attempt to reconnect if needed
        if (shouldReconnectRef.current && reconnectInterval > 0) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError(err as Event);
    }
  }, [commodity, horizon, reconnectInterval, onMessage, onError, onConnect, onDisconnect]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  const subscribe = useCallback((commodity: string, horizon: number) => {
    sendMessage({
      action: 'subscribe',
      commodity,
      horizon,
    });
  }, [sendMessage]);

  const requestForecast = useCallback((commodity: string, horizon: number) => {
    sendMessage({
      action: 'forecast',
      commodity,
      horizon,
    });
  }, [sendMessage]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    requestForecast,
  };
}

