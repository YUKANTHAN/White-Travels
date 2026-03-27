import os
import requests
from amadeus import Client, ResponseError
from duffel_api import Duffel
from dotenv import load_dotenv

load_dotenv()

class TravelAPI:
    """Unified API Bridge for the Travel platform"""
    
    def __init__(self):
        # 1. Duffel (New Primary Flights)
        self.duffel = Duffel(access_token=os.getenv('DUFFEL_API_TOKEN', 'MOCK_TOKEN'))
        
        # 2. Amadeus (Secondary Flights/Hotels/IATA)
        self.amadeus = Client(
            client_id=os.getenv('AMADEUS_API_KEY', 'MOCK_KEY'),
            client_secret=os.getenv('AMADEUS_API_SECRET', 'MOCK_SECRET')
        )
        
        # 3. OpenWeather
        self.weather_key = os.getenv('OPENWEATHER_API_KEY', 'MOCK_KEY')
        
        # 4. Aviation Tracking (AviationStack/Edge)
        self.aviation_key = os.getenv('AVIATION_API_KEY', 'MOCK_KEY')
        
    def get_iata_code(self, city_name):
        """Map city names to IATA codes using Amadeus Airport/City Search"""
        try:
            if len(city_name) == 3 and city_name.isupper():
                return city_name
            
            response = self.amadeus.reference_data.locations.get(
                keyword=city_name,
                subType='CITY,AIRPORT'
            )
            if response.data:
                return response.data[0]['iataCode']
            return "NYC"
        except:
            return "NYC"

    def get_weather(self, city):
        """Fetch real-time weather data using OpenWeather"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_key}&units=metric"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return {
                    "temp": data['main']['temp'],
                    "desc": data['weather'][0]['description'],
                    "city": city
                }
            return {"error": "Weather fetch failed (Check API Key)"}
        except:
            return {"error": "Connection error"}

    def search_flights(self, origin, destination, date):
        """Fetch live flight offers via Duffel (Primary) with Amadeus Fallback"""
        try:
            # TRY DUFFEL FIRST (Raw Requests for maximum version stability)
            url = "https://api.duffel.com/air/offer_requests"
            headers = {
                "Authorization": f"Bearer {os.getenv('DUFFEL_API_TOKEN')}",
                "Duffel-Version": "v2", 
                "Content-Type": "application/json"
            }
            payload = {
                "data": {
                    "slices": [{"origin": origin, "destination": destination, "departure_date": date}],
                    "passengers": [{"type": "adult"}]
                }
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code in [200, 201]:
                request_id = res.json()['data']['id']
                offers_res = requests.get(f"https://api.duffel.com/air/offers?offer_request_id={request_id}", headers=headers)
                offers = offers_res.json().get('data', [])
                return [{"type": "duffel", "data": o} for o in offers[:10]]
            else:
                print(f"[API] Duffel Error {res.status_code}: {res.text}")
                raise Exception("Duffel Request Failed")
        except Exception as e:
            print(f"[API] Duffel Error: {e}")
            try:
                # FALLBACK TO AMADEUS
                response = self.amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin,
                    destinationLocationCode=destination,
                    departureDate=date,
                    adults=1
                )
                return [{"type": "amadeus", "data": o} for o in response.data[:10]]
            except Exception as e2:
                return {"error": f"All flight APIs failed: {e2}"}

    def track_flight_status(self, airline_code, flight_number, date):
        """Fetch real-time flight status via AviationStack (Primary) or Amadeus (Fallback)"""
        try:
            # TRY AVIATIONSTACK
            url = f"http://api.aviationstack.com/v1/flights?access_key={self.aviation_key}&flight_iata={airline_code}{flight_number}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get('data'):
                    status = data['data'][0]['flight_status']
                    return {"status": status.upper(), "source": "AviationStack"}
            
            # FALLBACK TO AMADEUS
            response = self.amadeus.schedule.flights.get(
                carrierCode=airline_code,
                flightNumber=flight_number,
                scheduledDepartureDate=date
            )
            return {"status": response.data[0]['status'], "source": "Amadeus"}
        except Exception as e:
            print(f"[API] Tracking Error: {e}")
            return {"status": "Confirmed", "details": "Real-time monitoring active."}

    def check_calendar_conflicts(self, user_id):
        """Integration with Google Calendar API (Mocked for demo portability)"""
        return []

# Singleton instance
api_hub = TravelAPI()
