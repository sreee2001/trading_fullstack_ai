"""
WebSocket endpoint for real-time forecast updates.

This module implements WebSocket support for broadcasting real-time
forecast updates to connected clients.
"""

import json
import asyncio
from typing import Set, Dict, Any
from datetime import datetime, date
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from fastapi.exceptions import HTTPException

from api.models.forecast import ForecastRequest, ForecastResponse, Prediction
from api.services.model_service import get_model_service
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["WebSocket"])

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

# Connection metadata
connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, metadata: Dict[str, Any] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_metadata[websocket] = metadata or {}
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/forecast")
async def websocket_forecast_endpoint(
    websocket: WebSocket,
    commodity: str = Query(None, description="Commodity to subscribe to (WTI, BRENT, NG)"),
    horizon: int = Query(7, ge=1, le=30, description="Forecast horizon in days")
):
    """
    WebSocket endpoint for real-time forecast updates.
    
    **Connection:**
    - Connect to: `ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7`
    - Supports query parameters: `commodity` (WTI, BRENT, NG), `horizon` (1-30)
    
    **Message Format:**
    - Client can send: `{"action": "subscribe", "commodity": "WTI", "horizon": 7}`
    - Server sends: Forecast updates as JSON
    
    **Example Response:**
    ```json
    {
        "type": "forecast",
        "commodity": "WTI",
        "forecast_date": "2025-01-01",
        "horizon": 7,
        "predictions": [...],
        "timestamp": "2025-01-01T12:00:00Z"
    }
    ```
    """
    metadata = {
        "commodity": commodity,
        "horizon": horizon,
        "connected_at": datetime.utcnow().isoformat()
    }
    
    await manager.connect(websocket, metadata)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to forecast WebSocket",
            "commodity": commodity,
            "horizon": horizon,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        # Handle incoming messages
        while True:
            try:
                # Wait for message from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                    continue
                
                action = message.get("action")
                
                if action == "subscribe":
                    # Update subscription
                    new_commodity = message.get("commodity", commodity)
                    new_horizon = message.get("horizon", horizon)
                    
                    if new_commodity and new_commodity.upper() in ["WTI", "BRENT", "NG"]:
                        metadata["commodity"] = new_commodity.upper()
                    if new_horizon and 1 <= new_horizon <= 30:
                        metadata["horizon"] = new_horizon
                    
                    manager.connection_metadata[websocket] = metadata
                    
                    await manager.send_personal_message({
                        "type": "subscription",
                        "status": "updated",
                        "commodity": metadata["commodity"],
                        "horizon": metadata["horizon"],
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                    
                    # Generate and send forecast
                    await send_forecast_update(websocket, metadata["commodity"], metadata["horizon"])
                
                elif action == "forecast":
                    # Request immediate forecast
                    req_commodity = message.get("commodity", metadata.get("commodity"))
                    req_horizon = message.get("horizon", metadata.get("horizon", 7))
                    
                    if not req_commodity:
                        await manager.send_personal_message({
                            "type": "error",
                            "message": "Commodity required for forecast request",
                            "timestamp": datetime.utcnow().isoformat()
                        }, websocket)
                        continue
                    
                    await send_forecast_update(websocket, req_commodity.upper(), req_horizon)
                
                elif action == "ping":
                    # Heartbeat
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}", exc_info=True)
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)


async def generate_forecast_response(commodity: str, horizon: int) -> ForecastResponse:
    """
    Generate a forecast response (shared logic for REST and WebSocket).
    
    Args:
        commodity: Commodity symbol (WTI, BRENT, NG)
        horizon: Forecast horizon in days
        
    Returns:
        ForecastResponse object
    """
    # Import here to avoid circular dependency
    from api.routes.forecast import forecast as generate_forecast_endpoint
    
    forecast_request = ForecastRequest(
        commodity=commodity,
        horizon=horizon,
        start_date=date.today().isoformat()
    )
    
    return await generate_forecast_endpoint(forecast_request)


async def send_forecast_update(websocket: WebSocket, commodity: str, horizon: int):
    """
    Generate and send a forecast update to a WebSocket client.
    
    Args:
        websocket: WebSocket connection
        commodity: Commodity symbol (WTI, BRENT, NG)
        horizon: Forecast horizon in days
    """
    try:
        forecast_response = await generate_forecast_response(commodity, horizon)
        
        # Send forecast update
        await manager.send_personal_message({
            "type": "forecast",
            "commodity": forecast_response.commodity,
            "forecast_date": forecast_response.forecast_date,
            "horizon": forecast_response.horizon,
            "predictions": [
                {
                    "date": pred.date,
                    "price": pred.price,
                    "confidence_lower": pred.confidence_lower,
                    "confidence_upper": pred.confidence_upper
                }
                for pred in forecast_response.predictions
            ],
            "model_name": forecast_response.model_name,
            "model_version": forecast_response.model_version,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    except Exception as e:
        logger.error(f"Error generating forecast update: {e}", exc_info=True)
        await manager.send_personal_message({
            "type": "error",
            "message": f"Failed to generate forecast: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)


async def broadcast_forecast_update(commodity: str, horizon: int = 7):
    """
    Broadcast a forecast update to all connected clients.
    
    This can be called from external services (e.g., scheduled tasks)
    to push forecast updates to all subscribers.
    
    Args:
        commodity: Commodity symbol (WTI, BRENT, NG)
        horizon: Forecast horizon in days
    """
    if not manager.active_connections:
        return
    
    # Generate forecast once
    try:
        forecast_response = await generate_forecast_response(commodity, horizon)
        
        # Broadcast to all connections subscribed to this commodity
        message = {
            "type": "forecast",
            "commodity": forecast_response.commodity,
            "forecast_date": forecast_response.forecast_date,
            "horizon": forecast_response.horizon,
            "predictions": [
                {
                    "date": pred.date,
                    "price": pred.price,
                    "confidence_lower": pred.confidence_lower,
                    "confidence_upper": pred.confidence_upper
                }
                for pred in forecast_response.predictions
            ],
            "model_name": forecast_response.model_name,
            "model_version": forecast_response.model_version,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Filter connections by commodity subscription
        for connection, metadata in manager.connection_metadata.items():
            if connection in manager.active_connections:
                subscribed_commodity = metadata.get("commodity")
                if not subscribed_commodity or subscribed_commodity == commodity:
                    await manager.send_personal_message(message, connection)
    
    except Exception as e:
        logger.error(f"Error broadcasting forecast update: {e}", exc_info=True)

