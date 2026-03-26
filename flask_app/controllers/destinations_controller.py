from flask_app import app
import os
import requests
from flask import render_template,redirect,url_for, jsonify, request
from flask_app.utils.api_clients import api_hub

url = "https://hotels4.p.rapidapi.com/properties/list"

headers = {
	"X-RapidAPI-Key": os.environ.get("FLASK_APP_API_KEY"),
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

@app.route('/destinations/cabo')
def destination_cabo():
    # Scouting weather for Cabo before rendering
    weather = api_hub.get_weather("Cabo San Lucas")
    return render_template('cabo.html', weather=weather)

@app.route('/searching/weather', methods=['POST'])
def get_search_weather():
    city = request.json.get('city', 'New York')
    return jsonify(api_hub.get_weather(city))

@app.route("/searching/cabo", methods=["POST"])
def search_cabo():
    try:
        if not os.environ.get("FLASK_APP_API_KEY"):
            raise Exception("No API Key")
        querystring = {"destinationId":"1640244","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
        "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
        r = requests.request("GET", url, headers=headers, params=querystring)
        return jsonify( r.json() )
    except:
        # High-quality Hackathon Mock Fallback
        return jsonify({
            "data": {
                "body": {
                    "searchResults": {
                        "results": [
                            {"name": "Cabo San Lucas Luxury Resort", "address": {"streetAddress": "Beachfront Rd", "locality": "Cabo", "countryName": "Mexico"}, "guestReviews": {"rating": "9.5"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750"}},
                            {"name": "Baja Paradise Hotel", "address": {"streetAddress": "Downtown Loop", "locality": "Cabo", "countryName": "Mexico"}, "guestReviews": {"rating": "8.8"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1566073771259-6a8506099945"}},
                            {"name": "Ocean View Suites", "address": {"streetAddress": "Ocean Drive", "locality": "Cabo", "countryName": "Mexico"}, "guestReviews": {"rating": "9.0"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1582719508461-905c673771fd"}}
                        ]
                    }
                }
            }
        })

@app.route('/destinations/london')
def destination_london():
    return render_template('london.html')

@app.route("/searching/london", methods=["POST"])
def search_london():
    try:
        if not os.environ.get("FLASK_APP_API_KEY"):
            raise Exception("No API Key")
        querystring = {"destinationId":"549499","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
        "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
        r = requests.request("GET", url, headers=headers, params=querystring)
        return jsonify( r.json() )
    except:
        return jsonify({
            "data": { "body": { "searchResults": { "results": [
                {"name": "The Londoner Hotel", "address": {"streetAddress": "Leicester Square", "locality": "London", "countryName": "UK"}, "guestReviews": {"rating": "9.2"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1517760444937-f6397edcbbcd"}},
                {"name": "Thames River Inn", "address": {"streetAddress": "Southbank", "locality": "London", "countryName": "UK"}, "guestReviews": {"rating": "8.5"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1551882547-ff43c61f3c33"}},
                {"name": "Regent Street Boutique", "address": {"streetAddress": "Mayfair", "locality": "London", "countryName": "UK"}, "guestReviews": {"rating": "9.8"}, "optimizedThumbUrls": {"srpDesktop": "https://images.unsplash.com/photo-1445019980597-93fa8acb246c"}}
            ] } } }
        })

@app.route('/destinations/tokyo')
def destination_tokyo():
    return render_template('tokyo.html')

@app.route("/searching/tokyo", methods=["POST"])
def search_tokyo():
    querystring = {"destinationId":"726784","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
    "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
    r = requests.request("GET", url, headers=headers, params=querystring)
    return jsonify( r.json() )

@app.route('/destinations/honolulu')
def destination_honolulu():
    return render_template('honolulu.html')

@app.route("/searching/honolulu", methods=["POST"])
def search_honolulu():
    querystring = {"destinationId":"1431094","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
    "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
    r = requests.request("GET", url, headers=headers, params=querystring)
    return jsonify( r.json() )

@app.route('/destinations/new_york_city')
def destination_new_york():
    return render_template('new_york.html')

@app.route("/searching/new_york_city", methods=["POST"])
def search_nyc():
    querystring = {"destinationId":"1506246","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
    "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
    r = requests.request("GET", url, headers=headers, params=querystring)
    return jsonify( r.json() )

@app.route('/destinations/paris')
def destination_paris():
    return render_template('paris.html')

@app.route("/searching/paris", methods=["POST"])
def search_paris():
    querystring = {"destinationId":"504261","pageNumber":"1","pageSize":"15","checkIn":f"{request.form['check_in']}",
    "checkOut":f"{request.form['check_out']}","adults1":f"{request.form['num_adults']}","sortOrder":"BEST_SELLER","locale":"en_US","currency":"USD"}
    r = requests.request("GET", url, headers=headers, params=querystring)
    return jsonify( r.json() )

@app.route('/home')
def home():
    return redirect(url_for('index')+"#home")

@app.route('/booking')
def booking():
    return redirect(url_for('index')+"#book")

@app.route('/packages')
def packages():
    return redirect(url_for('index')+"#packages")

@app.route('/contactus')
def contactus():
    return redirect(url_for('index')+"#contact")
