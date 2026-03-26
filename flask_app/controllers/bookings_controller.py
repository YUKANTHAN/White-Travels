from flask_app import app
from flask import redirect, request, session, url_for, render_template, flash, Response, stream_with_context, jsonify
import os
import json
import time
import random
from flask_app.models.users import User
from flask_app.models.bookings import Booking
from flask_app.agent_manager import agent
from flask_app.utils.api_clients import api_hub
from ai_agent_backend.deep_concierge import DeepConcierge

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

# --- TRAINS & HOTELS ---
@app.route('/trains')
def trains(): return render_template('trains.html')

@app.route('/hotels')
def hotels(): return render_template('hotels.html')

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
    try:
        with open('itinerary.json', 'r') as f:
            itinerary = json.load(f)[0]
        itinerary['status'] = 'CANCELLED'
        with open('itinerary.json', 'w') as f:
            json.dump([itinerary], f, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/itinerary/rebook', methods=['POST'])
def trigger_rebook_logic():
    import subprocess
    script_path = os.path.join('.agent', 'skills', 'travel-expert', 'scripts', 'rebook_logic.py')
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        return jsonify({"success": True, "output": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/booking/simulate', methods=['POST'])
def create_simulated_booking():
    data = request.get_json()
    new_flight = {
        "status": "Confirmed",
        "flight_no": data.get('flight_no', 'AA123'),
        "pnr": "SIM-ITN-" + str(random.randint(1000, 9999))
    }
    with open('itinerary.json', 'w') as f:
        json.dump([new_flight], f, indent=4)
    return jsonify({"success": True, "itinerary": new_flight})

@app.route('/ai/plan', methods=['POST'])
def ai_plan():
    data = request.get_json()
    dest = data.get('destination', 'Unknown')
    date = data.get('date', 'TBD')
    budget = str(data.get('budget', '0'))
    companions = data.get('companions', 'Solo')
    
    plan_text = concierge.plan_trip(dest, date, budget, companions)
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
