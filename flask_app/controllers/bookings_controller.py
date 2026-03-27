from flask_app import app
from flask import redirect, request, session, url_for, render_template, flash, Response, stream_with_context, jsonify, send_file
import os
import json
import time
import random
import requests # Added for n8n integration

# Update this with your n8n Production Webhook URL
N8N_DISRUPTION_WEBHOOK = "https://your-n8n-instance.cloud/webhook/disruption-monitor"
N8N_CHECK_WEBHOOK = "https://suthan06it.app.n8n.cloud/webhook/check-disruption"
from flask_app.models.users import User
from flask_app.models.bookings import Booking
from flask_app.agent_manager import agent
from flask_app.utils.api_clients import api_hub
from ai_agent_backend.deep_concierge import DeepConcierge
from fpdf import FPDF
import io

# Singleton for AI Chat
concierge = DeepConcierge()

@app.route('/book', methods=["POST"])
def book():
    if not session.get('user_id') or session['user_id'] == 5:
        return redirect('/')
    if not Booking.validate(request.form):
        return redirect(url_for("index") + "#book_form")
    data = {
        **request.form,
        'user_id': session['user_id'],
        'type': 'General'
    }
    Booking.save(data)
    return redirect('/')

# --- FLIGHTS FLOW ---
@app.route('/flights')
def flights():
    return render_template('flights.html')

@app.route('/flights/search', methods=['POST'])
def flight_search():
    # RESOLVE IATA CODES FIRST: Corrects "London" -> "LON"
    origin = api_hub.get_iata_code(request.form.get('origin', 'NYC'))
    destination = api_hub.get_iata_code(request.form.get('destination', 'LON'))
    
    # Use dynamic tomorrow date for best real-world availability
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    real_flights = api_hub.search_flights(origin, destination, tomorrow)
    display_flights = []
    
    if isinstance(real_flights, list) and len(real_flights) > 0:
        for result in real_flights:
            res_type = result['type']
            offer = result['data']
            
            try:
                if res_type == 'duffel':
                    slice_data = offer['slices'][0]
                    segment = slice_data['segments'][0]
                    display_flights.append({
                        'airline': segment.get('operating_carrier', {}).get('iata_code', 'XX'),
                        'flight_no': segment.get('operating_carrier_flight_number', '000'),
                        'time': segment.get('departing_at', '').split('T')[1][:5] if 'T' in segment.get('departing_at', '') else "--:--",
                        'price': f"${offer.get('total_amount', '0.00')}",
                        'class': "Economy",
                        'is_real': True
                    })
                elif res_type == 'amadeus':
                    itinerary = offer['itineraries'][0]
                    segment = itinerary['segments'][0]
                    display_flights.append({
                        'airline': segment['carrierCode'],
                        'flight_no': segment['carrierCode'] + segment['number'],
                        'time': segment['departure']['at'].split('T')[1][:5],
                        'price': f"${offer['price']['total']}",
                        'class': segment.get('cabin', 'Economy'),
                        'is_real': True
                    })
            except Exception as e:
                print(f"[UI] Parsing error for {res_type}: {e}")
                continue
    
    if not display_flights:
        # Dynamic Hackathon Mock fallback if API fails
        display_flights = [
            {'airline': 'SkyHigh Air', 'flight_no': 'AA101', 'time': '08:00 AM', 'price': '$450', 'class': 'Economy', 'is_real': False},
            {'airline': 'Global Connect', 'flight_no': 'BA202', 'time': '11:30 AM', 'price': '$620', 'class': 'Business', 'is_real': False},
            {'airline': 'SwiftJet', 'flight_no': 'DL303', 'time': '03:15 PM', 'price': '$380', 'class': 'Economy', 'is_real': False},
            {'airline': 'Oceanic Airways', 'flight_no': 'UA404', 'time': '07:45 PM', 'price': '$510', 'class': 'Economy', 'is_real': False}
        ]

    return render_template('flight_details.html', origin=origin, destination=destination, flights=display_flights)

@app.route('/book_flight', methods=['POST'])
def book_flight():
    if not session.get('user_id') or session['user_id'] == 5:
        return redirect('/')
    data = {**request.form, 'user_id': session['user_id'], 'type': 'Flight'}
    Booking.save(data)
    flash("Flight booked successfully!", "success")
    return redirect('/')

@app.route('/book_package', methods=['POST'])
def book_package():
    if not session.get('user_id') or session['user_id'] == 5:
        return redirect('/')
    data = {**request.form, 'user_id': session['user_id'], 'type': 'Package'}
    data.pop('card_number', None)
    Booking.save(data)
    flash("Package booked successfully! Enjoy your trip.", "success")
    return redirect('/')

# --- TRAINS & HOTELS ---
@app.route('/trains')
def trains(): return render_template('trains.html')

@app.route('/trains/details', methods=['POST'])
def train_details():
    origin = request.form.get('origin', 'Central')
    destination = request.form.get('destination', 'Unknown Destination')
    trains_list = [
        {'name': 'Express Rail C1', 'duration': '2h 15m', 'departure': '08:00 AM', 'price': '$45'},
        {'name': 'Intercity FastTrain', 'duration': '3h 05m', 'departure': '10:30 AM', 'price': '$35'},
        {'name': 'Night Sleeper 7', 'duration': '8h 00m', 'departure': '11:00 PM', 'price': '$120'}
    ]
    return render_template('train_details.html', origin=origin, destination=destination, trains=trains_list)

@app.route('/hotels')
def hotels(): return render_template('hotels.html')

@app.route('/hotels/details', methods=['POST'])
def hotel_details():
    destination = request.form.get('destination', 'Unknown City')
    hotels_list = [
        {'name': f"{destination} Grand Hotel", 'stars': 5, 'price': '$250', 'description': 'Luxury accommodation right in the city center.'},
        {'name': f"Cozy {destination} Inn", 'stars': 3, 'price': '$120', 'description': 'Comfortable stay with complimentary breakfast.'},
        {'name': f"The Ritz {destination}", 'stars': 5, 'price': '$400', 'description': 'Five-star luxury amenities and pool access.'}
    ]
    return render_template('hotel_details.html', destination=destination, hotels=hotels_list)

@app.route('/book_hotel', methods=['POST'])
def book_hotel():
    if not session.get('user_id') or session['user_id'] == 5:
        return redirect('/')
    data = {**request.form, 'user_id': session['user_id']}
    data.pop('cvv', None)
    if 'card_number' in data:
        data['card_number'] = "**** **** **** " + data['card_number'][-4:]
    Booking.save(data)
    flash("Hotel booked successfully!", "success")
    return redirect('/')

# --- AI RECOVERY & TRAVEL EXPERT ---

@app.route('/itinerary/status')
def get_itinerary_status():
    try:
        with open('itinerary.json', 'r') as f:
            itinerary = json.load(f)[0]
        
        # Real-time Flight Monitor Bridge
        if itinerary.get('flight_no') and '-' not in itinerary['flight_no']:
            code, num = itinerary['flight_no'][:2], itinerary['flight_no'][2:]
            real_status = api_hub.track_flight_status(code, num, "2026-03-26")
            
            if "status" in real_status and real_status['status'] in ['DELAYED', 'CANCELLED']:
                itinerary['status'] = real_status['status'].upper()
                with open('itinerary.json', 'w') as f:
                    json.dump([itinerary], f, indent=4)
        return jsonify(itinerary)
    except:
        return jsonify({"status": "No Active Itinerary"})

@app.route('/itinerary/disruption', methods=['POST'])
def trigger_itinerary_disruption():
    print(f"[AGENT]: Pinging n8n for real-time disaster check...")
    try:
        with open('itinerary.json', 'r') as f:
            itinerary = json.load(f)[0]
            
        payload = {
            "pnr": itinerary.get("pnr"),
            "transport_id": itinerary.get("flight_no") or itinerary.get("train_no") or "Unknown",
            "route": f"from {itinerary.get('origin', 'Origin')} to {itinerary.get('destination', 'Dest')}",
            "dest": itinerary.get('destination', 'Unknown')
        }
        
        # Step 1: Trigger the n8n Workflow
        response = requests.post("https://suthan06it.app.n8n.cloud/webhook/check-disruption", json=payload, timeout=40)
        
        if response.status_code == 200:
            result = response.json()
            
            # Step 2: If AI found a disaster, update your local files
            if result.get("status") == "DISRUPTED":
                # Create the recovery itinerary based on the AI's alternative booking
                recovery = {
                    "status": "REBOOKED",
                    "passenger_name": itinerary.get("passenger_name", "Primary Passenger"),
                    "flight_no": "AI-RECOVERY",
                    "disruption_reason": result.get("reason", "Disrupted by Crisis Agent"),
                    "details": str(result.get("alternative_booking", "Crisis Stay or Alternative Transport"))
                }
                with open('itinerary.json', 'w') as f:
                    json.dump([recovery], f, indent=4)
                print(f"[SUCCESS]: AI Rebooked alternative due to: {result.get('reason')}")
                return jsonify({"success": True, "status": "CANCELLED", "reason": result.get('reason')})
            else:
                print("[LIVE]: No disruptions found by AI Search.")
                return jsonify({"success": True, "status": "CONFIRMED", "reason": "No disruptions found in location."})
                
        else:
            print(f"[ERROR]: n8n returned status {response.status_code}")
            return jsonify({"success": True, "status": "CANCELLED", "reason": f"n8n AI Cloud unreachable (HTTP {response.status_code})"})
            
    except requests.exceptions.RequestException as e:
        print(f"[ALERT]: Connection failed. Check if Ngrok is running! {e}")
        return jsonify({"success": True, "status": "CANCELLED", "reason": f"Live Network Error: {e}"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/itinerary/rebook', methods=['POST'])
def trigger_rebook_logic():
    # --- ACTIVATE N8N BRAIN ---
    try:
        with open('itinerary.json', 'r') as f:
            booking_data = json.load(f)[0]
        
        # Add additional metadata for the AI Agent
        booking_data['passenger_email'] = "user@example.com"
        booking_data['dest'] = "Paris" # Mock destination for weather lookup

        # Send the "Ping" to n8n
        print(f"--- Pinging n8n Brain at {N8N_DISRUPTION_WEBHOOK} ---")
        response = requests.post(N8N_DISRUPTION_WEBHOOK, json=booking_data, timeout=10)
        
        # If n8n returns a recovery strategy right away
        n8n_result = response.json() if response.status_code == 200 else {}
        rebooking_strategy = n8n_result.get('rebooking_strategy', "n8n Brain: Processing fallback recovery options...")

        return jsonify({
            "success": True, 
            "output": f"[N8N RECOVERY]: {rebooking_strategy}",
            "n8n_status": response.status_code
        })
    except Exception as e:
        # Fallback to local script if n8n is unreachable
        print(f"n8n unreachable: {e}. Falling back to local rebooker.")
        import subprocess
        script_path = os.path.join('.agent', 'skills', 'travel-expert', 'scripts', 'rebook_logic.py')
        try:
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
            return jsonify({"success": True, "output": result.stdout})
        except:
            return jsonify({"error": str(e)})

@app.route('/booking/simulate', methods=['POST'])
def create_simulated_booking():
    data = request.get_json()
    new_flight = {
        "status": "Confirmed",
        "passenger_name": "J. Doe (Primary)",
        "seat": "12A",
        "class_type": "Economy",
        "gate": "D4",
        "boarding_time": "10:15 AM",
        "flight_no": data.get('flight_no', 'UA204'),
        "train_no": data.get('train_no', ''),
        "hotel": data.get('hotel', ''),
        "pnr": "SIM-ITN-" + str(random.randint(1000, 9999)),
        # NEW AGENT FEATURES
        "budget_limit": 2500,
        "budget_spent": random.randint(300, 600),
        "carbon_kg": "450kg",
        "visa_status": "Processing Draft..."
    }
    with open('itinerary.json', 'w') as f:
        json.dump([new_flight], f, indent=4)
    return jsonify({"success": True, "itinerary": new_flight})

@app.route('/itinerary/offline')
def download_crisis_card():
    # Feature 4: Crisis Card (PDF Generation)
    try:
        with open('itinerary.json', 'r') as f:
            data = json.load(f)[0]
        
        pdf = FPDF()
        pdf.add_page()
        
        # Background color
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(0, 0, 210, 297, 'F')
        
        # Header
        pdf.set_font("Arial", 'B', 28)
        pdf.set_text_color(15, 23, 42) 
        pdf.cell(0, 30, "WHITE TRAVELS", ln=True, align='C')
        
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(56, 189, 248) # #38bdf8
        pdf.cell(0, 10, "OFFLINE CRISIS CARD", ln=True, align='C')
        pdf.ln(10)
        
        # Passenger Box
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 15, f" PASSENGER: {data.get('passenger_name', '---')}", ln=True, fill=True)
        pdf.ln(5)
        
        # Details Table-like layout
        pdf.set_text_color(15, 23, 42)
        pdf.set_font("Arial", 'B', 12)
        
        # Row 1
        pdf.cell(95, 12, f"PNR: {data.get('pnr', '---')}", border='B')
        pdf.cell(10, 12, "") # Spacer
        pdf.cell(90, 12, f"STATUS: {data.get('status', '---').upper()}", border='B', ln=True)
        
        # Row 2
        pdf.set_font("Arial", '', 11)
        pdf.cell(95, 12, f"Flight No: {data.get('flight_no', '---') or 'N/A'}", border='B')
        pdf.cell(10, 12, "")
        pdf.cell(90, 12, f"Train No: {data.get('train_no', '---') or 'N/A'}", border='B', ln=True)
        
        # Row 3
        pdf.cell(95, 12, f"Seat/Class: {data.get('seat', '---')} / {data.get('class_type', '---')}", border='B')
        pdf.cell(10, 12, "")
        pdf.cell(90, 12, f"Gate/Time: {data.get('gate', '---')} @ {data.get('boarding_time', '---')}", border='B', ln=True)
        
        # Row 4
        pdf.cell(0, 12, f"Visa Compliance: {data.get('visa_status', '---')}", border='B', ln=True)
        pdf.ln(15)
        
        # AI Footer
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 116, 139)
        footer_text = "This document is an AI-generated fallback for offline travel security. In the event of a total network dropout, present this card to airline or station staff. Your profile is autonomously tracked by White Travels AI Concierge."
        pdf.multi_cell(0, 8, footer_text, align='C')
        
        # Generated Time
        pdf.ln(5)
        import datetime
        pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')

        # Create response
        # FPDF output 'S' returns a string in Python 2 but bytes in Python 3
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=CRISIS_CARD_ITINERARY.pdf"
            }
        )
    except Exception as e:
        print(f"[PDF ERROR]: {e}")
        return jsonify({"error": "Failed to generate PDF. Check itinerary.json"}), 500

@app.route('/ai/plan', methods=['POST'])
def ai_plan():
    data = request.get_json()
    plan_text = concierge.plan_trip(data)
    return jsonify({"plan": plan_text})

@app.route('/ai/ask', methods=['POST'])
def ai_ask():
    data = request.get_json()
    return jsonify({
        "response": concierge.chat(data.get('prompt', '')),
        "agent": "DeepSeek-Concierge-v1",
        "tools_accessed": ["Amadeus", "Weather", "Calendar"]
    })

@app.route('/disruption/logs')
def stream_logs():
    def event_stream():
        last_index = 0
        while True:
            current_logs = agent.get_logs()
            if last_index < len(current_logs):
                for i in range(last_index, len(current_logs)):
                    yield f"data: {current_logs[i]}\n\n"
                last_index = len(current_logs)
            if last_index > 0 and "CONFIRM" in current_logs[-1]: break
            time.sleep(0.5)
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
