# WebSocket Test Cases

**Feature**: WebSocket Streaming for Real-time Forecast Updates  
**Date**: December 15, 2025  
**Status**: ✅ Implemented

---

## Overview

This document provides comprehensive test cases for the WebSocket streaming functionality, which enables real-time forecast updates to connected clients.

---

## Test Environment Setup

### Prerequisites
- FastAPI server running on `http://localhost:8000`
- WebSocket client (browser, Python, or test tool)
- API key (optional, for protected endpoints)

### WebSocket Endpoint
- **URL**: `ws://localhost:8000/api/v1/ws/forecast`
- **Query Parameters**:
  - `commodity` (optional): WTI, BRENT, NG
  - `horizon` (optional): 1-30 days (default: 7)

---

## Test Cases

### TC-WS-001: Basic WebSocket Connection

**Objective**: Verify WebSocket connection can be established

**Steps**:
1. Connect to `ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7`
2. Wait for connection confirmation

**Expected Result**:
- Connection established successfully
- Receive welcome message:
  ```json
  {
    "type": "connection",
    "status": "connected",
    "message": "Connected to forecast WebSocket",
    "commodity": "WTI",
    "horizon": 7,
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```

**Status**: ✅ Pass

---

### TC-WS-002: Subscribe to Forecast Updates

**Objective**: Verify subscription to forecast updates

**Steps**:
1. Connect to WebSocket
2. Receive welcome message
3. Send subscription message:
   ```json
   {
     "action": "subscribe",
     "commodity": "BRENT",
     "horizon": 14
   }
   ```

**Expected Result**:
- Receive subscription confirmation:
  ```json
  {
    "type": "subscription",
    "status": "updated",
    "commodity": "BRENT",
    "horizon": 14,
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```
- Receive forecast update (if model available)

**Status**: ✅ Pass

---

### TC-WS-003: Request Immediate Forecast

**Objective**: Verify ability to request immediate forecast

**Steps**:
1. Connect to WebSocket
2. Receive welcome message
3. Send forecast request:
   ```json
   {
     "action": "forecast",
     "commodity": "WTI",
     "horizon": 7
   }
   ```

**Expected Result**:
- Receive forecast response:
  ```json
  {
    "type": "forecast",
    "commodity": "WTI",
    "forecast_date": "2025-12-15",
    "horizon": 7,
    "predictions": [...],
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```

**Status**: ✅ Pass (if models available)

---

### TC-WS-004: Ping/Pong Heartbeat

**Objective**: Verify heartbeat mechanism works

**Steps**:
1. Connect to WebSocket
2. Send ping message:
   ```json
   {
     "action": "ping"
   }
   ```

**Expected Result**:
- Receive pong response:
  ```json
  {
    "type": "pong",
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```

**Status**: ✅ Pass

---

### TC-WS-005: Invalid JSON Handling

**Objective**: Verify error handling for invalid JSON

**Steps**:
1. Connect to WebSocket
2. Send invalid JSON: `invalid json`

**Expected Result**:
- Receive error message:
  ```json
  {
    "type": "error",
    "message": "Invalid JSON format",
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```
- Connection remains open

**Status**: ✅ Pass

---

### TC-WS-006: Unknown Action Handling

**Objective**: Verify error handling for unknown actions

**Steps**:
1. Connect to WebSocket
2. Send unknown action:
   ```json
   {
     "action": "unknown_action"
   }
   ```

**Expected Result**:
- Receive error message:
  ```json
  {
    "type": "error",
    "message": "Unknown action: unknown_action",
    "timestamp": "2025-12-15T12:00:00Z"
  }
  ```
- Connection remains open

**Status**: ✅ Pass

---

### TC-WS-007: Multiple Simultaneous Connections

**Objective**: Verify support for multiple connections

**Steps**:
1. Open connection 1: `ws://...?commodity=WTI&horizon=7`
2. Open connection 2: `ws://...?commodity=BRENT&horizon=14`
3. Verify both receive welcome messages

**Expected Result**:
- Both connections established
- Each receives appropriate welcome message
- Connections operate independently

**Status**: ✅ Pass

---

### TC-WS-008: Connection Cleanup on Disconnect

**Objective**: Verify proper cleanup on disconnect

**Steps**:
1. Connect to WebSocket
2. Close connection
3. Verify connection removed from active connections

**Expected Result**:
- Connection removed from active connections
- No memory leaks
- Server logs disconnect event

**Status**: ✅ Pass

---

### TC-WS-009: Forecast Update Broadcasting

**Objective**: Verify broadcast functionality (if implemented)

**Steps**:
1. Connect multiple clients
2. Trigger broadcast (via API or scheduled task)
3. Verify all subscribed clients receive update

**Expected Result**:
- All subscribed clients receive forecast update
- Only clients subscribed to relevant commodity receive update

**Status**: ⚠️ Requires external trigger (scheduled task or API call)

---

### TC-WS-010: Reconnection Handling

**Objective**: Verify client can reconnect after disconnect

**Steps**:
1. Connect to WebSocket
2. Disconnect
3. Reconnect
4. Verify new connection works

**Expected Result**:
- Reconnection successful
- New welcome message received
- Previous connection state cleared

**Status**: ✅ Pass

---

## Manual Testing

### Using Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7"
    async with websockets.connect(uri) as websocket:
        # Receive welcome
        welcome = await websocket.recv()
        print("Welcome:", welcome)
        
        # Subscribe
        await websocket.send(json.dumps({
            "action": "subscribe",
            "commodity": "WTI",
            "horizon": 7
        }))
        
        # Receive subscription confirmation
        response = await websocket.recv()
        print("Subscription:", response)

asyncio.run(test_websocket())
```

### Using Browser JavaScript

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/forecast?commodity=WTI&horizon=7');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({ action: 'subscribe', commodity: 'WTI', horizon: 7 }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('Error:', error);
};
```

---

## Performance Tests

### TC-WS-PERF-001: Connection Latency

**Objective**: Measure connection establishment time

**Expected**: < 100ms

**Status**: ⚠️ Requires measurement

---

### TC-WS-PERF-002: Message Throughput

**Objective**: Measure messages per second

**Expected**: > 100 messages/second

**Status**: ⚠️ Requires measurement

---

### TC-WS-PERF-003: Concurrent Connections

**Objective**: Test maximum concurrent connections

**Expected**: Support 100+ concurrent connections

**Status**: ⚠️ Requires load testing

---

## Known Limitations

1. **Authentication**: WebSocket endpoint does not currently require API key (may be added in future)
2. **Rate Limiting**: No rate limiting on WebSocket connections (may be added in future)
3. **Broadcasting**: Manual broadcast requires external trigger (scheduled task or API call)

---

## Test Results Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC-WS-001 | ✅ Pass | Basic connection works |
| TC-WS-002 | ✅ Pass | Subscription works |
| TC-WS-003 | ✅ Pass | Forecast request works (if models available) |
| TC-WS-004 | ✅ Pass | Ping/pong works |
| TC-WS-005 | ✅ Pass | Invalid JSON handled |
| TC-WS-006 | ✅ Pass | Unknown action handled |
| TC-WS-007 | ✅ Pass | Multiple connections supported |
| TC-WS-008 | ✅ Pass | Cleanup works |
| TC-WS-009 | ⚠️ Pending | Requires external trigger |
| TC-WS-010 | ✅ Pass | Reconnection works |

**Overall**: 9/10 test cases passing (90%)

---

**Last Updated**: December 15, 2025

