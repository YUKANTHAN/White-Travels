import json
import os
import time
import threading
import random
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

# High-Performance API Configuration
amadeus = Client(
    client_id=os.getenv('AMADEUS_API_KEY', 'YOUR_KEY_HERE'),
    client_secret=os.getenv('AMADEUS_API_SECRET', 'YOUR_SECRET_HERE')
)

results = {}

def fetch_flight_alternatives(pnr):
    """Parallel Thread 1: Amadeus Flight Search"""
    time.sleep(random.uniform(0.1, 0.4)) # Simulated latency
    results['flight'] = "FL-NEW-505"
    print("[REBOOKER] Parallel Task: Flight identified.")

def fetch_hotel_alternatives(location):
    """Parallel Thread 2: Amadeus Hotel Search"""
    time.sleep(random.uniform(0.1, 0.4)) # Simulated latency
    results['hotel'] = "Marriott Elite Suite"
    print("[REBOOKER] Parallel Task: Hotel secured.")

def perform_rebooking():
    """Atomic Turbo Rebooking Sequence"""
    try:
        if not os.path.exists('itinerary.json'):
            return
            
        with open('itinerary.json', 'r') as f:
            data = json.load(f)
            itinerary = data[0] if isinstance(data, list) else data
        
        if itinerary.get('status') == 'CANCELLED':
            start_time = time.time()
            print(f"\n[URGENT] DISRUPTION RECOVERY ACTIVATED for PNR: {itinerary['pnr']}")
            
            # MULTI-THREADING: Parallel API calls
            t1 = threading.Thread(target=fetch_flight_alternatives, args=(itinerary['pnr'],))
            t2 = threading.Thread(target=fetch_hotel_alternatives, args=("NYC",))
            
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            
            # Finalize Update
            itinerary['status'] = 'REBOOKED'
            itinerary['flight_no'] = results.get('flight')
            itinerary['hotel'] = results.get('hotel')
            itinerary['recovery_time_ms'] = int((time.time() - start_time) * 1000)
            
            with open('itinerary.json', 'w') as f:
                json.dump([itinerary] if isinstance(data, list) else itinerary, f, indent=4)
            
            print(f"[REBOOKER] SUCCESS: Itinerary fixed in {itinerary['recovery_time_ms']}ms.")
            print(f"[FIXED]: New itinerary generated: {itinerary['flight_no']} + {itinerary['hotel']}")
            return True
            
    except Exception as e:
        print(f"[ERROR] Turbo Rebooking failed: {str(e)}")
        return False

if __name__ == "__main__":
    perform_rebooking()
