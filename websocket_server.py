import asyncio
import websockets
import json
from datetime import datetime
from typing import Set, Optional

class WebSocketServer:
    def __init__(self, host='', port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.last_event_data: Optional[dict] = None
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        print(f"Client {websocket.remote_address} connected. Total clients: {len(self.clients)}")
        
        # Send the last event data to newly connected client if available
        if self.last_event_data:
            await self.send_to_client(websocket, self.last_event_data)
    
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.discard(websocket)
        print(f"Client {websocket.remote_address} disconnected. Total clients: {len(self.clients)}")
    
    async def send_to_client(self, websocket, data):
        """Send data to a specific client"""
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister(websocket)
    
    async def broadcast(self, data):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
        
        # Store the last event
        self.last_event_data = data
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Send to all clients
        disconnected_clients = set()
        for client in self.clients.copy():
            try:
                await client.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister(client)
    
    async def handle_client(self, websocket, path=None):
        """Handle a new client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                # Handle incoming messages from clients if needed
                print(f"Received message from {websocket.remote_address}: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    def get_last_event(self):
        """Get the last event data"""
        return self.last_event_data
    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        return await websockets.serve(self.handle_client, self.host, self.port)

# Global instance
ws_server = WebSocketServer()

async def publish_session_data(data):
    """Function to be called from relay.py to publish data"""
    await ws_server.broadcast(data)