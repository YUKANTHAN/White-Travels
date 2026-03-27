import time
import json
import os
import requests
import threading
from .api_clients import api_hub
from ..models.contacts import Contact

# Configuration
MONITOR_INTERVAL_SECONDS = 30 # For demo: check every 30 seconds
N8N_CHECK_WEBHOOK = "https://suthan06it.app.n8n.cloud/webhook/check-disruption"

def scan_itineraries_proactively():
    """Background loop that periodically checks the health of the active itinerary."""
    print(f"\n[SENTRY] --- Autonomous AI Monitor Activated (Scanning every {MONITOR_INTERVAL_SECONDS}s) ---\n")
    
    while True:
        try:
            itinerary_path = os.path.join(os.getcwd(), 'itinerary.json')
            if not os.path.exists(itinerary_path):
                time.sleep(MONITOR_INTERVAL_SECONDS)
                continue

            with open(itinerary_path, 'r') as f:
                data = json.load(f)
                if not data:
                    time.sleep(MONITOR_INTERVAL_SECONDS)
                    continue
                itinerary = data[0]

            # Only track if NOT already in AWAITING_CONSENT or REBOOKED status
            if itinerary.get('status', 'CONFIRMED').upper() not in ['CONFIRMED', 'DELAYED']:
                time.sleep(MONITOR_INTERVAL_SECONDS)
                continue

            # Real-time Flight Monitoring Bridge (using Airline API / AviationStack)
            if itinerary.get('flight_no') and '-' not in itinerary['flight_no']:
                code, num = itinerary['flight_no'][:2], itinerary['flight_no'][2:]
                
                print(f"[SENTRY] Tracking live status for: {code}{num}...")
                real_status = api_hub.track_flight_status(code, num, "2026-03-26")
                
                # JURY REQUIREMENT: PROACTIVE EVENT-DRIVEN TRIGGER
                if "status" in real_status and real_status['status'] in ['DELAYED', 'CANCELLED']:
                    print(f"\n🚨 [SENTRY ALERT] Disruption detected proactively for {itinerary['passenger_name']}! Triggering AI Recovery...\n")
                    
                    # 1. Update local status immediately
                    itinerary['status'] = real_status['status'].upper()
                    itinerary['disruption_reason'] = f"The Sentinel detected a {real_status['status']} event via Airline API."
                    
                    with open(itinerary_path, 'w') as f:
                        json.dump([itinerary], f, indent=4)

                    # 2. Trigger the AI Agent (n8n or Local) without user intervention
                    try:
                        payload = {
                            "pnr": itinerary.get("pnr"),
                            "transport_id": itinerary['flight_no'],
                            "route": f"from {itinerary.get('origin', 'Origin')} to {itinerary.get('destination', 'Dest')}",
                            "status": real_status['status']
                        }
                        response = requests.post(N8N_CHECK_WEBHOOK, json=payload, timeout=10)
                        
                        if response.status_code == 200:
                            result = response.json()
                            reason = result.get("reason", "Proactive AI Recovery Triggered")
                            
                            # Update to AWAITING_CONSENT with the proposed alternative
                            itinerary['status'] = 'AWAITING_CONSENT'
                            itinerary['temp_flight'] = result.get("alternative_flight", "WT-SENTINEL-FIX")
                            itinerary['disruption_reason'] = reason
                            
                            with open(itinerary_path, 'w') as f:
                                json.dump([itinerary], f, indent=4)

                            # 3. PUSH ALERT TO CUSTOMER WHATSAPP
                            customer_phone = os.environ.get('CUSTOMER_PHONE_NUMBER', "+919025066367")
                            notif_msg = (
                                f"🔴 *AUTONOMOUS ALERT:* Disruption detected for your travel! 🔴\n\n"
                                f"Reason: {reason}\n"
                                f"Solution Found: {itinerary['temp_flight']}\n\n"
                                f"Approve this change in your dashboard now."
                            )
                            Contact.send_whatsapp_notification(customer_phone, notif_msg)
                            
                    except Exception as re:
                        print(f"[SENTRY] Autonomous Recovery failed: {re}")

        except Exception as e:
            print(f"[SENTRY ERROR] Monitor failure: {e}")
            
        time.sleep(MONITOR_INTERVAL_SECONDS)

def start_sentry_monitor():
    """Starts the sentiment monitor in a background thread."""
    thread = threading.Thread(target=scan_itineraries_proactively, daemon=True)
    thread.start()
