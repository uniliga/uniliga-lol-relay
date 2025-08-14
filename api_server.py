from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from websocket_server import ws_server
import asyncio
from typing import Optional
from pydantic import BaseModel

# We'll get the replay system from a global variable set by main.py
_replay_system = None

def set_replay_system(replay_system):
    """Set the replay system instance"""
    global _replay_system
    _replay_system = replay_system

def get_replay_system():
    """Get the replay system instance"""
    return _replay_system

app = FastAPI(title="League of Legends Champion Select API", version="1.0.0")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request bodies
class ReplayRequest(BaseModel):
    filename: str
    start_index: Optional[int] = 0
    end_index: Optional[int] = None
    speed: Optional[float] = 1.0

class ReplaySpeedRequest(BaseModel):
    speed: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "League of Legends Champion Select API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "websocket_clients": len(ws_server.clients)}

@app.get("/session/current")
async def get_current_session():
    """Get the current/last champion select session data"""
    last_event = ws_server.get_last_event()
    if last_event is None:
        raise HTTPException(status_code=404, detail="No session data available")
    return last_event

@app.get("/session/status")
async def get_session_status():
    """Get session status information"""
    last_event = ws_server.get_last_event()
    if last_event is None:
        return {
            "has_session": False,
            "websocket_clients": len(ws_server.clients)
        }
    
    return {
        "has_session": True,
        "phase": last_event.get("timer", {}).get("phase"),
        "websocket_clients": len(ws_server.clients),
        "timestamp": last_event.get("timestamp"),
        "is_replay": last_event.get("_replay", {}).get("is_replay", False)
    }

@app.get("/teams/my")
async def get_my_team():
    """Get my team data"""
    last_event = ws_server.get_last_event()
    if last_event is None:
        raise HTTPException(status_code=404, detail="No session data available")
    
    my_team = last_event.get("myTeam", [])
    return {"team": my_team}

@app.get("/teams/their")
async def get_their_team():
    """Get their team data"""
    last_event = ws_server.get_last_event()
    if last_event is None:
        raise HTTPException(status_code=404, detail="No session data available")
    
    their_team = last_event.get("theirTeam", [])
    return {"team": their_team}

@app.get("/bans")
async def get_bans():
    """Get ban information"""
    last_event = ws_server.get_last_event()
    if last_event is None:
        raise HTTPException(status_code=404, detail="No session data available")
    
    bans = last_event.get("bans", {})
    return {
        "myTeamBans": bans.get("myTeamBans", []),
        "theirTeamBans": bans.get("theirTeamBans", [])
    }

# Replay endpoints
@app.get("/replay/status")
async def get_replay_status():
    """Get current replay status"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    return replay_system.get_status()

@app.post("/replay/load")
async def load_replay_file(request: ReplayRequest):
    """Load events from a replay file"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    success = replay_system.load_events_from_file(request.filename)
    if not success:
        raise HTTPException(status_code=404, detail=f"Could not load file: {request.filename}")
    
    return {
        "message": f"Successfully loaded {len(replay_system.events)} events from {request.filename}",
        "total_events": len(replay_system.events)
    }

@app.post("/replay/play")
async def play_replay(request: ReplayRequest, background_tasks: BackgroundTasks):
    """Start playing a replay"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    if not replay_system.events:
        raise HTTPException(status_code=400, detail="No events loaded. Load a file first.")
    
    if replay_system.is_playing:
        raise HTTPException(status_code=400, detail="Replay is already playing")
    
    # Set replay speed if provided
    if request.speed:
        replay_system.set_replay_speed(request.speed)
    
    # Start replay in background
    background_tasks.add_task(
        replay_system.play_events, 
        request.start_index, 
        request.end_index
    )
    
    return {
        "message": "Replay started",
        "start_index": request.start_index,
        "end_index": request.end_index or len(replay_system.events),
        "speed": replay_system.replay_speed
    }

@app.post("/replay/stop")
async def stop_replay():
    """Stop the current replay"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    replay_system.stop_replay()
    return {"message": "Replay stopped"}

@app.post("/replay/speed")
async def set_replay_speed(request: ReplaySpeedRequest):
    """Set the replay speed"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    replay_system.set_replay_speed(request.speed)
    return {
        "message": f"Replay speed set to {replay_system.replay_speed}x",
        "speed": replay_system.replay_speed
    }

@app.post("/replay/event/{event_index}")
async def play_single_event(event_index: int):
    """Play a single event by index"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    success = await replay_system.play_single_event(event_index)
    if not success:
        raise HTTPException(status_code=400, detail=f"Could not play event {event_index}")
    
    return {"message": f"Played event {event_index}"}

@app.get("/replay/events")
async def list_replay_events(limit: int = 20):
    """List loaded replay events"""
    replay_system = get_replay_system()
    if not replay_system:
        raise HTTPException(status_code=503, detail="Replay system not available")
    
    events = replay_system.list_events(limit)
    return {
        "events": events,
        "total_events": len(replay_system.events),
        "showing": min(limit, len(replay_system.events))
    }

@app.on_event("startup")
async def startup_event():
    """Start the WebSocket server when the API starts"""
    print("Starting API server...")
    # The WebSocket server will be started in the main function

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when the API shuts down"""
    print("Shutting down API server...")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)