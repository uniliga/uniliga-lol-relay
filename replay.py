import json
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional
import queue
from util import team_to_url, bans_to_url

class EventReplay:
    def __init__(self, data_queue: queue.Queue):
        self.data_queue = data_queue
        self.events: List[Dict] = []
        self.is_playing = False
        self.current_index = 0
        self.replay_speed = 1.0  # 1.0 = normal speed, 2.0 = double speed, 0.5 = half speed
        
    def load_events_from_file(self, filename: str) -> bool:
        """Load events from a JSON file where each line is a separate JSON object"""
        try:
            self.events = []
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            event = json.loads(line)
                            self.events.append({
                                'event': event,
                                'line_number': line_num,
                                'original_timestamp': event.get('data', {}).get('timer', {}).get('internalNowInEpochMs', 0)
                            })
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON on line {line_num}: {e}")
                            continue
            
            print(f"Loaded {len(self.events)} events from {filename}")
            return len(self.events) > 0
        except FileNotFoundError:
            print(f"File {filename} not found")
            return False
        except Exception as e:
            print(f"Error loading events: {e}")
            return False
    
    def calculate_delays(self) -> List[float]:
        """Calculate delays between events based on timestamps"""
        if len(self.events) < 2:
            return [0] * len(self.events)
        
        delays = [0]  # First event has no delay
        
        for i in range(1, len(self.events)):
            current_timestamp = self.events[i]['original_timestamp']
            previous_timestamp = self.events[i-1]['original_timestamp']
            
            # If timestamps are available and valid, calculate delay
            if current_timestamp > 0 and previous_timestamp > 0:
                delay_ms = current_timestamp - previous_timestamp
                delay_seconds = delay_ms / 1000.0
                # Cap delays at reasonable limits (max 10 seconds between events)
                delay_seconds = min(delay_seconds, 10.0)
                delays.append(max(delay_seconds, 0.1))  # Minimum 100ms delay
            else:
                # Default delay if timestamps are not available
                delays.append(1.0)  # 1 second default
        
        return delays
    
    def process_event_data(self, event: Dict) -> Dict:
        """Process event data the same way as the live relay"""
        data = event['event']['data']
        
        # Mutate the data with URLs (same as in relay)
        if data.get('myTeam'):
            myTeam = team_to_url(data.get('myTeam'))
            data['myTeam'] = myTeam
        
        if data.get('theirTeam'):
            theirTeam = team_to_url(data.get('theirTeam'))
            data['theirTeam'] = theirTeam

        # Handle bans
        if data.get('bans'):
            if data['bans'].get('myTeamBans'):
                myTeamBans = bans_to_url(data.get('bans').get('myTeamBans'))
                data['bans']['myTeamBans'] = myTeamBans
            
            if data['bans'].get('theirTeamBans'):
                theirTeamBans = bans_to_url(data.get('bans').get('theirTeamBans'))
                data['bans']['theirTeamBans'] = theirTeamBans
        
        # Add replay metadata
        event['event']['_replay'] = {
            'is_replay': True,
            'replay_timestamp': datetime.now().isoformat(),
            'original_timestamp': data.get('timer', {}).get('internalNowInEpochMs', 0)
        }
        
        event['event']['data'] = data
        
        return event
    
    async def play_events(self, start_index: int = 0, end_index: Optional[int] = None) -> None:
        """Play events from start_index to end_index"""
        if not self.events:
            print("No events loaded")
            return
        
        if end_index is None:
            end_index = len(self.events)
        
        end_index = min(end_index, len(self.events))
        start_index = max(0, start_index)
        
        if start_index >= end_index:
            print("Invalid start/end indices")
            return
        
        self.is_playing = True
        self.current_index = start_index
        
        print(f"Starting replay from event {start_index} to {end_index}")
        print(f"Replay speed: {self.replay_speed}x")
        
        delays = self.calculate_delays()
        
        try:
            for i in range(start_index, end_index):
                if not self.is_playing:
                    print("Replay stopped")
                    break
                
                self.current_index = i
                event = self.events[i]
                
                # Process the event data
                processed_data = self.process_event_data(event)
                
                # Send to WebSocket queue
                try:
                    self.data_queue.put(processed_data['event'], block=False)
                    print(f"Replayed event {i+1}/{len(self.events)} - Line {event['line_number']}")
                except queue.Full:
                    print(f"Queue full, skipping event {i+1}")
                
                # Wait for the calculated delay (adjusted by replay speed)
                if i < len(delays) - 1:  # Don't wait after the last event
                    delay = delays[i + 1] / self.replay_speed
                    await asyncio.sleep(delay)
                
        except Exception as e:
            print(f"Error during replay: {e}")
        finally:
            self.is_playing = False
            print("Replay finished")
    
    async def play_single_event(self, index: int) -> bool:
        """Play a single event by index"""
        if not self.events or index < 0 or index >= len(self.events):
            print(f"Invalid event index: {index}")
            return False
        
        event = self.events[index]
        processed_data = self.process_event_data(event)
        
        try:
            self.data_queue.put(processed_data['event'], block=False)
            print(f"Replayed single event {index+1}/{len(self.events)} - Line {event['line_number']}")
            return True
        except queue.Full:
            print("Queue full, cannot replay event")
            return False
    
    def stop_replay(self):
        """Stop the current replay"""
        self.is_playing = False
    
    def set_replay_speed(self, speed: float):
        """Set the replay speed multiplier"""
        self.replay_speed = max(0.1, min(speed, 10.0))  # Clamp between 0.1x and 10x
        print(f"Replay speed set to {self.replay_speed}x")
    
    def get_status(self) -> Dict:
        """Get current replay status"""
        return {
            'is_playing': self.is_playing,
            'current_index': self.current_index,
            'total_events': len(self.events),
            'replay_speed': self.replay_speed,
            'events_loaded': len(self.events) > 0
        }
    
    def list_events(self, limit: int = 10) -> List[Dict]:
        """List loaded events with basic info"""
        events_info = []
        for i, event in enumerate(self.events[:limit]):
            timer = event['data'].get('timer', {})
            events_info.append({
                'index': i,
                'line_number': event['line_number'],
                'phase': timer.get('phase', 'Unknown'),
                'timestamp': event['original_timestamp'],
                'my_team_size': len(event['data'].get('myTeam', [])),
                'their_team_size': len(event['data'].get('theirTeam', []))
            })
        return events_info

# Global replay instance
replay_system: Optional[EventReplay] = None

def initialize_replay_system(data_queue: queue.Queue):
    """Initialize the global replay system"""
    global replay_system
    replay_system = EventReplay(data_queue)
    return replay_system

def get_replay_system() -> Optional[EventReplay]:
    """Get the global replay system instance"""
    return replay_system