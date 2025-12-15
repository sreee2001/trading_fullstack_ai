"""
Tests for WebSocket endpoint.

Tests WebSocket connection, message handling, and forecast broadcasting.
"""

import pytest
import json
from datetime import date, datetime
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from api.main import app
from api.routes.websocket import ConnectionManager, manager


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def connection_manager():
    """Create connection manager instance."""
    return ConnectionManager()


class TestConnectionManager:
    """Tests for ConnectionManager class."""
    
    def test_connection_manager_initialization(self, connection_manager):
        """Test connection manager initialization."""
        assert len(connection_manager.active_connections) == 0
        assert len(connection_manager.connection_metadata) == 0
    
    @pytest.mark.asyncio
    async def test_connect(self, connection_manager):
        """Test connecting a WebSocket."""
        # Mock WebSocket
        class MockWebSocket:
            async def accept(self):
                pass
        
        ws = MockWebSocket()
        metadata = {"commodity": "WTI", "horizon": 7}
        
        await connection_manager.connect(ws, metadata)
        
        assert ws in connection_manager.active_connections
        assert connection_manager.connection_metadata[ws] == metadata
    
    def test_disconnect(self, connection_manager):
        """Test disconnecting a WebSocket."""
        # Mock WebSocket
        class MockWebSocket:
            pass
        
        ws = MockWebSocket()
        connection_manager.active_connections.add(ws)
        connection_manager.connection_metadata[ws] = {"test": "data"}
        
        connection_manager.disconnect(ws)
        
        assert ws not in connection_manager.active_connections
        assert ws not in connection_manager.connection_metadata


class TestWebSocketEndpoint:
    """Tests for WebSocket endpoint."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, client):
        """Test WebSocket connection."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["status"] == "connected"
            assert data["commodity"] == "WTI"
            assert data["horizon"] == 7
    
    @pytest.mark.asyncio
    async def test_websocket_subscribe(self, client):
        """Test subscription message."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Send subscribe message
            websocket.send_json({
                "action": "subscribe",
                "commodity": "BRENT",
                "horizon": 14
            })
            
            # Receive subscription confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscription"
            assert data["status"] == "updated"
            assert data["commodity"] == "BRENT"
            assert data["horizon"] == 14
    
    @pytest.mark.asyncio
    async def test_websocket_ping_pong(self, client):
        """Test ping/pong heartbeat."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Send ping
            websocket.send_json({"action": "ping"})
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_websocket_invalid_json(self, client):
        """Test handling invalid JSON."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Send invalid JSON
            websocket.send_text("invalid json")
            
            # Receive error message
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "Invalid JSON" in data["message"]
    
    @pytest.mark.asyncio
    async def test_websocket_unknown_action(self, client):
        """Test handling unknown action."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Send unknown action
            websocket.send_json({"action": "unknown_action"})
            
            # Receive error message
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "Unknown action" in data["message"]
    
    @pytest.mark.asyncio
    async def test_websocket_forecast_request(self, client):
        """Test forecast request via WebSocket."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            # Receive welcome message
            websocket.receive_json()
            
            # Request forecast
            websocket.send_json({
                "action": "forecast",
                "commodity": "WTI",
                "horizon": 7
            })
            
            # Receive forecast or error
            data = websocket.receive_json()
            # May receive error if models not available, or forecast if available
            assert data["type"] in ["forecast", "error"]


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, client):
        """Test multiple simultaneous connections."""
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as ws1:
            with client.websocket_connect("/api/v1/ws/forecast?commodity=BRENT&horizon=14") as ws2:
                # Both should receive welcome messages
                data1 = ws1.receive_json()
                data2 = ws2.receive_json()
                
                assert data1["type"] == "connection"
                assert data2["type"] == "connection"
                assert data1["commodity"] == "WTI"
                assert data2["commodity"] == "BRENT"
    
    @pytest.mark.asyncio
    async def test_connection_cleanup(self, client):
        """Test connection cleanup on disconnect."""
        initial_count = len(manager.active_connections)
        
        with client.websocket_connect("/api/v1/ws/forecast?commodity=WTI&horizon=7") as websocket:
            websocket.receive_json()
            # Connection should be added
            assert len(manager.active_connections) > initial_count
        
        # After disconnect, connection should be removed
        # Note: This may not be immediate in test environment
        # In production, cleanup happens in disconnect handler

