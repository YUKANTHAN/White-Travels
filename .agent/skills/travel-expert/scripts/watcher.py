import json
import os
import time
import subprocess

ITINERARY_FILE = 'itinerary.json'
REBOOK_SCRIPT = '.agent/skills/travel-expert/scripts/rebook_logic.py'

def watch_itinerary():
    """Silent real-time watcher for disruption events."""
    print("[TURBO] Background Watcher Active. Listening to itinerary.json...")
    
    last_mtime = 0
    if os.path.exists(ITINERARY_FILE):
        last_mtime = os.path.getmtime(ITINERARY_FILE)
    
    while True:
        try:
            current_mtime = os.path.getmtime(ITINERARY_FILE)
            if current_mtime > last_mtime:
                # File was modified, check status
                with open(ITINERARY_FILE, 'r') as f:
                    data = json.load(f)
                    status = data[0].get('status') if isinstance(data, list) else data.get('status')
                    
                    if status == 'CANCELLED':
                        # TRIGGER REBOOKER IMMEDIATELY
                        print(f"[TURBO] Status: CANCELLED detected. Firing Rebooker...")
                        subprocess.run(['python', REBOOK_SCRIPT], capture_output=False)
                        
                        # Re-read status after execution
                        with open(ITINERARY_FILE, 'r') as f:
                            new_data = json.load(f)
                            new_status = new_data[0].get('status') if isinstance(new_data, list) else new_data.get('status')
                            new_flight = new_data[0].get('flight_no') if isinstance(new_data, list) else new_data.get('flight_no')
                            
                            if new_status == 'REBOOKED':
                                print(f"[FIXED]: New itinerary generated: {new_flight}")
                
                last_mtime = current_mtime
            
            time.sleep(0.5) # Poll every 500ms
        except Exception as e:
            # Silently handle errors (e.g. file busy during write)
            time.sleep(0.1)
            continue

if __name__ == "__main__":
    watch_itinerary()
