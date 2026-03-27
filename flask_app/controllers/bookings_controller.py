from flask_app import app
from flask import redirect, request, session, url_for, render_template, flash, Response, stream_with_context, jsonify, send_file
import os
import json
import time
import random
import requests
from fpdf import FPDF
import io

# n8n Webhook URLs
N8N_DISRUPTION_WEBHOOK = "https://your-n8n-instance.cloud/webhook/disruption-monitor"
N8N_CHECK_WEBHOOK = "https://suthan06it.app.n8n.cloud/webhook/check-disruption"

from flask_app.models.users import User
from flask_app.models.bookings import Booking
from flask_app.models.contacts import Contact
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

@app.route('/itinerary/stream')
def stream_itinerary_updates():
    def event_stream():
        last_mtime = 0
        while True:
            try:
                current_mtime = os.path.getmtime('itinerary.json')
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    with open('itinerary.json', 'r') as f:
                        data = json.load(f)
                    yield f"data: {json.dumps(data)}\n\n"
                else:
                    # Heartbeat to keep connection alive
                    yield ":\n\n"
            except: pass
            time.sleep(1)
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

@app.route('/itinerary/status')
def get_itinerary_status():
    try:
        with open('itinerary.json', 'r') as f:
            itinerary = json.load(f)
        
        # Real-time Flight Monitor Bridge (for all active entries)
        for booking in itinerary:
            if booking.get('flight_no') and '-' not in booking['flight_no']:
                code, num = booking['flight_no'][:2], booking['flight_no'][2:]
                real_status = api_hub.track_flight_status(code, num, "2026-03-26")
                
                if "status" in real_status and real_status['status'] in ['DELAYED', 'CANCELLED']:
                    booking['status'] = real_status['status'].upper()
        
        with open('itinerary.json', 'w') as f:
            json.dump(itinerary, f, indent=4)
        
        return jsonify(itinerary)
    except (FileNotFoundError, json.JSONDecodeError, IndexError) as e:
        print(f"[ITINERARY] No active itinerary: {e}")
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
        try:
            response = requests.post(N8N_CHECK_WEBHOOK, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                # Create the recovery itinerary based on the AI's alternative booking
                alt_flight = result.get("alternative_flight", "ALT-FL-101")
                alt_train = result.get("alternative_train", "RECOVERY-TRAIN-B")
                reason = result.get("reason", "Crisis Agent Intervention")

                recovery = {
                    "status": "AWAITING_CONSENT",
                    "passenger_name": itinerary.get("passenger_name", "Primary Passenger"),
                    "flight_no": itinerary.get("flight_no"),
                    "train_no": itinerary.get("train_no"),
                    "temp_flight": alt_flight,
                    "temp_train": alt_train,
                    "disruption_reason": reason,
                    "details": str(result.get("alternative_booking", "Crisis Stay or Alternative Transport"))
                }
                with open('itinerary.json', 'w') as f:
                    json.dump([recovery], f, indent=4)
                        
                # --- IMMEDIATE CUSTOMER NOTIFICATION ---
                customer_phone = os.environ.get('CUSTOMER_PHONE_NUMBER', "+919025066367")
                notif_msg = (
                    f"❗ *Crisis Alert:* {reason}\n\n"
                    f"Our AI has proposed an alternative plan for you:\n"
                    f"✈️ *New Flight:* {alt_flight}\n"
                    f"🚆 *New Train:* {alt_train}\n\n"
                    f"Reply 'YES' in your dashboard to finalize this rebooking."
                )
                try:
                    Contact.send_whatsapp_notification(customer_phone, notif_msg)
                except Exception as ne:
                    print(f"WhatsApp Notify error: {ne}")

                print(f"[SUCCESS]: AI Proposed alternative due to: {reason}")
                return jsonify({"success": True, "status": "AWAITING_CONSENT", "reason": reason})
            else:
                print("[LIVE]: No disruptions found by AI Search.")
                return jsonify({"success": True, "status": "CONFIRMED", "reason": "No disruptions found in location."})
        except Exception as inner_ex:
            print(f"[N8N CALL FAIL]: {inner_ex}. Falling back to Demo.")

        # --- DEMO FALLBACK: PROACTIVE & SUSTAINABLE RECOVERY ---
        itinerary['status'] = 'CANCELLED'
        # Predictive + Sustainability Logic
        carbon_saved = 150 
        itinerary['disruption_reason'] = (
            "⚠️ [PREDICTIVE ALERT]: Severe sleet storm detected 4h out. "
            f"Switching to Rail will save {carbon_saved}kg CO2 (75% risk reduction). "
            "⚡ **[GREEN RECOVERY]** Agent is pre-holding a sleeper seat for safety."
        )
        itinerary['carbon_kg'] = f"{itinerary.get('carbon_kg','350kg')} (-{carbon_saved}kg)"
        
        with open('itinerary.json', 'w') as f:
            json.dump([itinerary], f, indent=4)
        
        return jsonify({
            "success": True, 
            "status": "CANCELLED", 
            "reason": itinerary['disruption_reason'],
            "carbon_saved": carbon_saved
        })
            
    except Exception as outer_e:
        print(f"[CRITICAL ERR]: {outer_e}")
        return jsonify({"error": str(outer_e), "success": False})

@app.route('/itinerary/approve', methods=['POST'])
def approve_itinerary_change():
    """Finalizes the rebooking after the customer grants consent via dashboard."""
    try:
        with open('itinerary.json', 'r') as f:
            data = json.load(f)
            itinerary = data[0] if isinstance(data, list) else data
        
        if itinerary.get('status') == 'AWAITING_CONSENT':
            # Finalize the change
            itinerary['flight_no'] = itinerary.pop('temp_flight', 'ALT-99')
            itinerary['train_no'] = itinerary.pop('temp_train', 'TRAIN-99')
            itinerary['status'] = 'REBOOKED_AND_CONFIRMED'
            itinerary['approved_at'] = time.ctime()
            
            with open('itinerary.json', 'w') as f:
                json.dump([itinerary] if isinstance(data, list) else itinerary, f, indent=4)
            
            # Send Final Confirmation WhatsApp
            customer_phone = os.environ.get('CUSTOMER_PHONE_NUMBER', "+919025066367")
            conf_msg = f"✅ *Rebooking Confirmed!* ✅\n\nYour new itinerary has been finalized:\n✈️ Flight: {itinerary['flight_no']}\n🚆 Train: {itinerary['train_no']}\n\nSafe travels!"
            try:
                Contact.send_whatsapp_notification(customer_phone, conf_msg)
            except: pass

            return jsonify({"success": True, "message": "Rebooking finalized successfully!"})
        else:
            return jsonify({"success": False, "message": "No pending rebooking request found."})
            
    except Exception as e:
        return jsonify({"error": str(e), "success": False})

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
        try:
            response = requests.post(N8N_DISRUPTION_WEBHOOK, json=booking_data, timeout=10)
            n8n_result = response.json() if response.status_code == 200 else {}
            rebooking_strategy = n8n_result.get('rebooking_strategy', "n8n Brain: Processing fallback recovery options...")

            # --- AUTO-NOTIFY CUSTOMER VIA WHATSAPP ---
            customer_phone = os.environ.get('CUSTOMER_PHONE_NUMBER', "+919025066367")
            whatsapp_msg = f"⚠️ *Travel Alert for {booking_data.get('passenger_name')}* ⚠️\n\nYour itinerary is being adjusted due to disruptions. \n\n*Current Strategy:* {rebooking_strategy}\n\nOur AI is monitoring your status 24/7. Check your dashboard for real-time updates! 🌍"
            
            try:
                Contact.send_whatsapp_notification(customer_phone, whatsapp_msg)
            except Exception as e:
                print(f"WhatsApp notification failed: {e}")

            return jsonify({
                "success": True, 
                "output": f"[N8N RECOVERY]: {rebooking_strategy}",
                "n8n_status": response.status_code
            })
        except Exception as n8n_err:
            print(f"n8n unreachable: {n8n_err}. Falling back to local rebooker.")
            
            import subprocess
            script_path = os.path.join('.agent', 'skills', 'travel-expert', 'scripts', 'rebook_logic.py')
            
            try:
                result = subprocess.run(['python', script_path], capture_output=True, text=True)
                output_text = result.stdout
                
                # --- AUTO-NOTIFY CUSTOMER VIA WHATSAPP (LOCAL FALLBACK) ---
                customer_phone = os.environ.get('CUSTOMER_PHONE_NUMBER', "+919025066367")
                
                prop_flight = f"WT-ALT-{random.randint(200,800)}"
                prop_train = "METRO-RECOV-12"
                
                booking_data['status'] = 'AWAITING_CONSENT'
                booking_data['temp_flight'] = prop_flight
                booking_data['temp_train'] = prop_train
                with open('itinerary.json', 'w') as f:
                    json.dump([booking_data], f, indent=4)

                whatsapp_msg = (
                    f"🔔 *Agent Alert: Flight Recovery In Progress* 🔔\n\n"
                    f"Disruption detected. Our autonomous system has proposed a re-routing:\n\n"
                    f"✈️ *Proposed Flight:* {prop_flight}\n"
                    f"🚆 *Proposed Train:* {prop_train}\n\n"
                    f"Please approve this in your dashboard to proceed."
                )
                try:
                    Contact.send_whatsapp_notification(customer_phone, whatsapp_msg)
                except Exception as w_e:
                     print(f"WhatsApp notification failed: {w_e}")

                return jsonify({"success": True, "output": f"Proposed Alternatives: {prop_flight}, {prop_train}"})
            except Exception as sub_e:
                return jsonify({"error": str(sub_e), "success": False})

    except Exception as outer_e:
        return jsonify({"error": str(outer_e), "success": False})

@app.route('/booking/simulate', methods=['POST'])
def create_simulated_booking():
    data = request.get_json()
    new_flight = {
        "status": "CONFIRMED",
        "passenger_name": data.get('passenger_name', 'J. Doe (Primary)'),
        "seat": f"{random.randint(1,40)}{random.choice('ABCDEF')}",
        "class_type": "Economy",
        "gate": f"{random.choice('ABCD')}{random.randint(1,10)}",
        "boarding_time": "10:15 AM",
        "flight_no": data.get('flight_no', f'WT-{random.randint(100,500)}'),
        "train_no": data.get('train_no', ''),
        "hotel": data.get('hotel', 'AI Selected Stay'),
        "origin": "Current",
        "destination": data.get('destination', 'Paris'),
        "pnr": "SIM-ITN-" + str(random.randint(1000, 9999)),
        # NEW AGENT FEATURES
        "budget_limit": 2500,
        "budget_spent": random.randint(300, 600),
        "carbon_kg": f"{random.randint(200, 600)}kg",
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
@app.route('/itinerary/offline')
def offline_crisis_card():
    """Generates a high-fidelity 'Master Itinerary' for the user to keep offline."""
    try:
        with open('itinerary.json', 'r') as f:
            data = json.load(f)
            itinerary = data[0] if isinstance(data, list) else data
        
        # A sleek, printable offline card template
        content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>White Travels | Master Itinerary Card</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.2/css/all.min.css">
            <style>
                body {{ font-family: 'Inter', sans-serif; background: #f8fafc; padding: 40px; color: #1e293b; }}
                .card {{ max-width: 600px; margin: 0 auto; background: white; border: 2px solid #38bdf8; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: #38bdf8; color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .row {{ display: flex; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }}
                .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; }}
                .value {{ font-size: 18px; font-weight: 700; }}
                .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; }}
                .pnr-box {{ background: #020617; color: #38bdf8; font-family: monospace; padding: 5px 15px; border-radius: 5px; font-size: 14px; }}
                @media print {{ .noprint {{ display: none; }} body {{ padding: 0; background: white; }} .card {{ box-shadow: none; border: 1px solid #eee; }} }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="header">
                    <i class="fas fa-paper-plane fa-3x" style="margin-bottom: 10px;"></i>
                    <h1 style="margin: 0;">MASTER RECOVERY CARD</h1>
                    <p style="margin: 5px 0 0; opacity: 0.8;">Autonomous AI Agentic Concierge</p>
                </div>
                <div class="content">
                    <div class="row">
                        <div class="label"><i class="fas fa-user"></i> PASSENGER</div>
                        <div class="value">{itinerary.get('passenger_name', 'Traveling Guest')}</div>
                    </div>
                    <div class="row">
                        <div class="label"><i class="fas fa-barcode"></i> PNR RECORD</div>
                        <div class="pnr-box">{itinerary.get('pnr', 'PNR-XXXXXX')}</div>
                    </div>
                    <div class="row">
                        <div>
                            <div class="label">FLIGHT / TRAIN</div>
                            <div class="value">{itinerary.get('flight_no', 'N/A')} / {itinerary.get('train_no', 'N/A')}</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="label">GATE / SEAT</div>
                            <div class="value">{itinerary.get('gate', '---')} / {itinerary.get('seat', '---')}</div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="label">CURRENT STATE</div>
                        <div class="value" style="color: #10b981;">{itinerary.get('status', 'CONFIRMED')}</div>
                    </div>
                    <div style="background: #fffbeb; border: 1px solid #fef3c7; padding: 15px; border-radius: 10px; margin-top: 20px;">
                        <h4 style="margin: 0; color: #d97706; font-size: 14px;"><i class="fas fa-shield-alt"></i> AI RECOVERY PROTOCOL:</h4>
                        <p style="font-size: 12px; color: #92400e; margin: 5px 0 0;">
                            If connectivity is lost, present this card at any White Travels terminal. Our AI Sentinel (WT-Agent) has already synchronized your rebooking options to the global flight database.
                        </p>
                    </div>
                </div>
                <div class="footer">
                    &copy; 2026 White Travels | Powered by Deep Concierge v4.0
                </div>
            </div>
            <div style="text-align: center; margin-top: 30px;" class="noprint">
                <button onclick="window.print()" style="background: #38bdf8; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                    <i class="fas fa-print"></i> Print Recovery Card
                </button>
            </div>
        </body>
        </html>
        """
        return content
    except Exception as e:
        return f"<h1>Recovery Offline: {str(e)}</h1>"
