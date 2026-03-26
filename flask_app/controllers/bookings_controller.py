from flask_app import app
from flask import redirect,request,session,url_for,render_template,flash
import os
import smtplib
from email.message import EmailMessage
from flask_app.models.users import User
from flask_app.models.bookings import Booking
from flask_app.agent_manager import agent
from flask import Response, stream_with_context, jsonify
import json
import time

@app.route('/book', methods=["POST"])
def book():
    if session['user_id'] == 5:
        return redirect('/')
    if not Booking.validate(request.form):
        return redirect(url_for("index")+"#book_form")
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
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    # Generate multiple varied flight options
    flights = [
        {'airline': 'SkyHigh Air', 'time': '08:00 AM', 'price': '$450', 'class': 'Economy'},
        {'airline': 'Global Connect', 'time': '11:30 AM', 'price': '$620', 'class': 'Business'},
        {'airline': 'SwiftJet', 'time': '03:15 PM', 'price': '$380', 'class': 'Economy'},
        {'airline': 'Oceanic Airways', 'time': '07:45 PM', 'price': '$510', 'class': 'Economy'},
        {'airline': 'Premium Wings', 'time': '10:00 PM', 'price': '$1,200', 'class': 'First Class'}
    ]
    return render_template('flight_details.html', origin=origin, destination=destination, flights=flights)

@app.route('/book_flight', methods=['POST'])
def book_flight():
    if session.get('user_id') == 5 or not session.get('user_id'):
        return redirect('/')
    data = {
        **request.form,
        'user_id': session['user_id'],
        'type': 'Flight'
    }
    Booking.save(data)
    flash("Flight booked successfully!", "success")
    return redirect('/')

# --- TRAINS FLOW ---
@app.route('/trains')
def trains():
    return render_template('trains.html')

@app.route('/trains/details', methods=['POST'])
def train_details():
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    # Generate multiple varied train options
    trains = [
        {'name': 'Express Rail 101', 'departure': '07:00 AM', 'duration': '4h 30m', 'price': '$85'},
        {'name': 'Silver Bullet', 'departure': '10:15 AM', 'duration': '3h 15m', 'price': '$140'},
        {'name': 'Regional Tracker', 'departure': '01:45 PM', 'duration': '6h 00m', 'price': '$55'},
        {'name': 'Midnight Cruiser', 'departure': '11:00 PM', 'duration': '5h 30m', 'price': '$95'}
    ]
    return render_template('train_details.html', origin=origin, destination=destination, trains=trains)

@app.route('/book_train', methods=['POST'])
def book_train():
    if session.get('user_id') == 5 or not session.get('user_id'):
        return redirect('/')
    data = {
        **request.form,
        'user_id': session['user_id'],
        'type': 'Train'
    }
    Booking.save(data)
    flash("Train booked successfully!", "success")
    return redirect('/')

# --- HOTELS FLOW ---
@app.route('/hotels')
def hotels():
    return render_template('hotels.html')

@app.route('/hotels/details', methods=['POST'])
def hotel_details():
    destination = request.form.get('destination')
    # Generate multiple varied hotel options
    hotels = [
        {'name': 'Grand Palace Resort', 'stars': 5, 'price': '$350', 'description': 'Luxury at its best with panoramic views.'},
        {'name': 'Urban Stay Boutique', 'stars': 4, 'price': '$180', 'description': 'Modern comfort in the heart of the city.'},
        {'name': 'Budget Inn & Suites', 'stars': 3, 'price': '$95', 'description': 'Clean, affordable, and close to transit.'},
        {'name': 'Seaside Sanctuary', 'stars': 5, 'price': '$420', 'description': 'Private beach access and world-class spa.'}
    ]
    return render_template('hotel_details.html', destination=destination, hotels=hotels)

@app.route('/book_hotel', methods=['POST'])
def book_hotel():
    if session.get('user_id') == 5 or not session.get('user_id'):
        return redirect('/')
    # In a real app, we would process payment here
    data = {
        **request.form,
        'user_id': session['user_id']
    }
    # Remove sensitive info before saving
    data.pop('cvv', None)
    if 'card_number' in data:
        data['card_number'] = "**** **** **** " + data['card_number'][-4:]
    
    Booking.save(data)
    flash("Hotel booked successfully!", "success")
    return redirect('/')

# --- PACKAGES FLOW ---
@app.route('/book_package', methods=['POST'])
def book_package():
    if session.get('user_id') == 5 or not session.get('user_id'):
        return redirect('/')
    data = {
        **request.form,
        'user_id': session['user_id'],
        'type': 'Package'
    }
    Booking.save(data)
    flash("Package booked successfully!", "success")
    return redirect('/')

# --- AI RECOVERY SYSTEM ROUTES ---

@app.route('/disruption/trigger', methods=['POST'])
def trigger_disruption():
    event = request.get_json()  # e.g. {"id": "FL202"}
    # Call the agent manager's ReAct loop to generate the structured recovery plan
    result = agent.run_react_loop(event)
    
    # Return the full structured response: status, plan, confidence, reason, alternatives_considered
    return jsonify(result)

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
            
            # If the loop is finished and logs are processed, break (simple for demo)
            if last_index > 0 and "CONFIRM" in current_logs[-1]:
                break
            time.sleep(0.5)
            
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
