import asyncio
import os
import uvicorn
from websocket_server import ws_server
from api_server import app, set_replay_system
import threading
import time
import queue
from lcu_driver import Connector
import json
from util import *
from datetime import datetime
from replay import initialize_replay_system
import aiohttp
import ssl

# Queue for communication between LCU relay and WebSocket server
data_queue = queue.Queue()

# Live Client API configuration
LIVE_CLIENT_API_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"
LIVE_CLIENT_POLLING_RATE = 0.5  # seconds between polls

async def start_websocket_server():
    """Start the WebSocket server"""
    server = await ws_server.start_server()
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

def start_rest_api():
    """Start the REST API server"""
    print("Starting REST API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

async def poll_live_client_api():
    """Poll the Live Client API and relay data via WebSocket"""
    # Create SSL context that doesn't verify certificates (for self-signed certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            try:
                async with session.get(LIVE_CLIENT_API_URL, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        players = data['allPlayers']
                        url_players = live_players_to_url(players)
                        data['allPlayers'] = url_players
                        
                        # Add to queue for WebSocket publishing
                        try:
                            data_queue.put({
                                'data': data, 
                                'eventType': 'LIVE_CLIENT_DATA', 
                                'uri': '/liveclientdata/allgamedata'
                            }, block=False)
                            print("Live Client data queued for WebSocket publishing")
                        except queue.Full:
                            print("Queue is full, dropping Live Client data")
                        except Exception as e:
                            print(f"Error queuing Live Client data: {e}")
                    else:
                        print(f"Live Client API returned status {response.status}")
                        
            except aiohttp.ClientError as e:
                # API not available (game not running)
                pass
            except asyncio.TimeoutError:
                print("Live Client API request timed out")
            except Exception as e:
                print(f"Error polling Live Client API: {e}")
            
            # Wait before next poll
            await asyncio.sleep(LIVE_CLIENT_POLLING_RATE)

async def process_data_queue():
    """Process data from the queue and publish via WebSocket"""
    while True:
        try:
            # Check for new data every 100ms
            await asyncio.sleep(0.1)
            
            # Process all available data in the queue
            while not data_queue.empty():
                try:
                    data = data_queue.get_nowait()
                    await ws_server.broadcast(data)
                    print("Data published via WebSocket")
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"Error publishing data: {e}")
        except Exception as e:
            print(f"Error in data processing: {e}")

def start_relay():
    """Start the LCU relay in a separate thread with its own event loop"""
    # Create and set an event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        print("Starting League Client relay...")
        
        # Initialize data as in relay.py
        champions_url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/champion.json'
        summoners_url = f'{DDRAGON_BASE_URL}{DDRAGON_VERSION}/data/en_US/summoner.json'
            
        summoners_lookup = download_json(summoners_url, '.', 'summoner.json')
        champions_lookup = download_json(champions_url, '.', 'champion.json')

        now = datetime.now()
        record_timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        with open(f'record{record_timestamp}.json', 'w') as f:
            pass  # Create empty file

        # Create connector - it will use the event loop we just set
        connector = Connector()

        @connector.ready
        async def connect(connection):
            print('LCU API is ready to be used.')

        @connector.ws.register('/lol-summoner/v1/current-summoner', event_types=('UPDATE',))
        async def icon_changed(connection, event):
            print(f'The summoner {event.data["displayName"]} was updated.')
            
        @connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
        async def session_changed(connection, event):
            data = event.data.copy()  # Make a copy to avoid modifying original
            
            with open('sessiondump.json', 'a') as file:
                file.write(json.dumps({'data': data, 'eventType': 'UPDATE', 'uri': '/lol-champ-select/v1/session' }))
                file.write('\n')  
            
            if data.get('myTeam'):
                myTeam = await team_add_names(connection, data.get('myTeam'))
                data['myTeam'] = myTeam
                
            if data.get('theirTeam'):
                theirTeam = await team_add_names(connection, data.get('theirTeam'))
                data['theirTeam'] = theirTeam
            
            # Fearless
            fearless = []
            if os.path.exists('fearless.json'):
                with open('fearless.json', 'r', encoding='utf-8') as file:
                    fearless = json.load(file)
            print(fearless)
            
            teams = data.get('myTeam') + data.get('theirTeam')
            champions = get_all_champions(data.get('actions'), teams)
            print(champions)
            
            combined_champions = champions + fearless
            combined_champions_unique = fearless_unique(combined_champions)
            
            
            with open('fearless.json', 'w', encoding='utf-8') as file:
                json.dump(combined_champions_unique, file, indent=2, ensure_ascii=False)
            
            
            fearless_wo = fearless_remove_current(combined_champions_unique, champions)
            print(fearless_wo)
            data['fearless'] = fearless_wo
            
            
            # Save raw data to files
            with open(f'record{record_timestamp}.json', 'a') as file:
                file.write(json.dumps({'data': data, 'eventType': 'UPDATE', 'uri': '/lol-champ-select/v1/session' }))
                file.write('\n') 

            
            # Mutate the data with URLs
            if data.get('myTeam'):
                myTeam = team_to_url(data.get('myTeam'))
                data['myTeam'] = myTeam
            
            if data.get('theirTeam'):
                theirTeam = team_to_url(data.get('theirTeam'))
                data['theirTeam'] = theirTeam

            
            
            
            
            # Handle bans
            # print(data)
            # if data.get('bans'):
            #     print(data['bans'])
            #     if data['bans'].get('myTeamBans'):
            #         myTeamBans = bans_to_url(data.get('bans').get('myTeamBans'))
            #         data['bans']['myTeamBans'] = myTeamBans
                
            #     if data['bans'].get('theirTeamBans'):
            #         theirTeamBans = bans_to_url(data.get('bans').get('theirTeamBans'))
            #         data['bans']['theirTeamBans'] = theirTeamBans
            myTeamSize = len(myTeam)
            print(myTeamSize)
            bans = handle_bans(data.get('actions'), myTeamSize)
            print(bans)
            data['bans'] = bans
            print('-----------------------------------')
            print(bans)
            
            # Save mutated data
            with open('sessiondumpurls.json', 'a') as file:
                file.write(json.dumps({'data': data, 'eventType': 'UPDATE', 'uri': '/lol-champ-select/v1/session' }))
                file.write('\n')

            # Add to queue for WebSocket publishing
            try:
                data_queue.put({'data': data, 'eventType': 'UPDATE', 'uri': '/lol-champ-select/v1/session' }, block=False)
                print("Data queued for WebSocket publishing")
            except queue.Full:
                print("Queue is full, dropping data")
            except Exception as e:
                print(f"Error queuing data: {e}")

        
        @connector.ws.register('/lol-end-of-game/v1/eog-stats-block', event_types=('CREATE','UPDATE'))
        async def end_of_game_stats(connection, event):
            data = event.data.copy() 
            print(f'End of Game:{data}')
            
            teams = data.get('teams')
            url_teams = post_teams_to_url(teams)
            data['teams'] = url_teams
            
            
            
            tk = []
            if os.path.exists('tk.json'):
                with open('tk.json', 'r', encoding='utf-8') as file:
                    tk = json.load(file)
                    
            tk = create_tk_data(teams, tk)
            data['tk'] = tk
            
            with open('tk.json', 'w', encoding='utf-8') as file:
                json.dump(tk, file, indent=2, ensure_ascii=False)
            
            
            # Save raw data to files
            with open(f'record{record_timestamp}.json', 'a') as file:
                file.write(json.dumps({'data': data, 'eventType': 'CREATE', 'uri': '/lol-end-of-game/v1/eog-stats-block' }))
                file.write('\n') 
            
            try:
                data_queue.put({'data': data, 'eventType': 'CREATE', 'uri': '/lol-end-of-game/v1/eog-stats-block' }, block=False)
                print("Data queued for WebSocket publishing")
            except queue.Full:
                print("Queue is full, dropping data")
            except Exception as e:
                print(f"Error queuing data: {e}")
        
        
        @connector.close
        async def disconnect(connection):
            print('LCU relay finished')

        try:
            # Start the connector - this will use the loop we created and manage it
            connector.start()
        except KeyboardInterrupt:
            print("LCU relay stopped by user")
        except Exception as e:
            print(f"LCU relay error: {e}")
            
    except Exception as e:
        print(f"Error in relay thread: {e}")
        # If connector.start() didn't close the loop, close it manually
        if not loop.is_closed():
            loop.close()

async def main():
    """Main function to start all services"""
    print("Starting League of Legends Champion Select Monitor...")
    print("=" * 60)
    
    # Initialize replay system
    replay_system = initialize_replay_system(data_queue)
    set_replay_system(replay_system)  # Set it in the API module
    print("Replay system initialized")
    
    # Start WebSocket server
    websocket_task = asyncio.create_task(start_websocket_server())
    
    # Start data queue processor
    queue_processor_task = asyncio.create_task(process_data_queue())
    
    # Start REST API in a separate thread
    api_thread = threading.Thread(target=start_rest_api, daemon=True)
    api_thread.start()
    
    # Wait a moment for servers to start
    await asyncio.sleep(2)
    
    # Start LCU relay in a separate thread
    relay_thread = threading.Thread(target=start_relay, daemon=True)
    relay_thread.start()
    
    # Start Live Client API polling
    live_client_task = asyncio.create_task(poll_live_client_api())
    
    print("All services started!")
    print("=" * 60)
    print("WebSocket Server: ws://localhost:8765")
    print("REST API: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("LCU Relay: Monitoring League Client")
    print("Live Client API Polling: https://127.0.0.1:2999/liveclientdata/allgamedata")
    print("Test Client: Open test_client.html in your browser")
    print("=" * 60)
    print("🎬 REPLAY SYSTEM AVAILABLE:")
    print("- Load replay: POST /replay/load")
    print("- Start replay: POST /replay/play")
    print("- Stop replay: POST /replay/stop")
    print("- Replay status: GET /replay/status")
    print("=" * 60)
    print("Press Ctrl+C to stop all services")
    
    # Wait for all tasks (keeps the main thread alive)
    await asyncio.gather(websocket_task, queue_processor_task, live_client_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServers shutting down...")
    except Exception as e:
        print(f"Error: {e}")