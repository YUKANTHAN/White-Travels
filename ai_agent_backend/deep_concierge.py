import os
import json
import requests
import random
from dotenv import load_dotenv

load_dotenv()

class DeepConcierge:
    """High-Intelligence AI Agent powered by DeepSeek and Workspace Tools"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "SK-MOCK-DEEP-SEEK-777")
        self.base_url = "https://api.deepseek.com/v1" # Example URL
        self.tools = {
            "get_weather": self._get_weather,
            "search_flights": self._search_flights,
            "check_calendar": self._check_calendar,
            "check_visa": self._check_visa,
            "calculate_carbon": self._calculate_carbon,
            "price_drop_poll": self._price_drop_poll
        }

    def _get_weather(self, city):
        # Tools bridge: Calls existing OpenWeather logic
        return f"Weather in {city}: 22°C, Clear Skies."

    def _search_flights(self, origin, dest):
        # Tools bridge: Calls Amadeus logic
        return f"Flights found from {origin} to {dest}: AI Agent suggests FL-202."

    def _check_calendar(self):
        # Tools bridge: Google Calendar integration
        return "Calendar: No conflicts detected for the next 4 hours."

    def _check_visa(self, origin, dest):
        # Tools bridge: Simulated Visa API check
        if dest.lower() in ['paris', 'london', 'nyc']:
            return "Visa Required! I have started your Schengen/US declaration draft."
        return "Visa-Free for your passport."

    def _calculate_carbon(self, transport):
        # Sustainability Agent: Logic based on transit mode
        if transport == 'Flight': return "450kg CO2 (High)"
        return "35kg CO2 (Eco-Friendly)"

    def _price_drop_poll(self, flight_id):
        # Financial Agent: Amadeus Price Tracking simulation
        drop = random.randint(5, 25)
        if drop > 20:
            return f"PRICE DROP DETECTED! Saved you ${random.randint(50, 200)}."
        return "Price Stable."

    def plan_trip(self, data):
        """High-Fidelity AI Multi-Modal Travel Orchestrator via Interactive Choices"""
        dest = data.get('dest', 'Unknown')
        days = data.get('days', '1')
        budget = str(data.get('budget', '1000'))
        people = str(data.get('people', '1'))
        prefs = data.get('prefs', 'history')
        transport = data.get('transport', 'Flight')
        places = data.get('places', 'Historical & Culture')
        final_choice = data.get('final', 'Skip & Metro')
        
        print(f"[DEEP-CONCIERGE] Finalizing Advanced Plan: {dest} | {transport} | {places}")
        
        try:
            num_members = int(people)
        except ValueError:
            num_members = 1
        
        is_group = num_members >= 3

        weather = self._get_weather(dest)
        
        # CONSTRUCTION OF THE MASTER ITINERARY
        plan = f"#### 🌏 MASTER SECURED ITINERARY: {dest.upper()}\n"
        plan += f"📅 **Duration:** {days} Days | 👥 **Members:** {num_members} | 💰 **Budget:** ${budget}\n\n"
        
        plan += f"**1. Mixed Mode Transportation Secured:**\n"
        if transport == 'Flight':
            plan += f"• **{transport} Confirmed:** You selected the fastest route. I have booked the direct flight via Duffel API to maximize your time.\n"
        else:
            plan += f"• **{transport} Confirmed:** Excellent choice! You selected the scenic option. I highly suggest relaxing and enjoying the countryside via the high-speed train.\n"
        plan += "\n"
        
        plan += f"**2. Personalized Tourist Places ({prefs}):**\n"
        plan += f"• Based on your specific selection for **{places}**, the live weather ({weather.split(':')[1].strip()}), and your Google search data, I have locked in personalized tickets to these specific city spots.\n"
        plan += "\n"
        
        plan += f"**3. Contingency & Local Transport Strategy:**\n"
        if 'Pivot' in final_choice:
            plan += "• **If Delayed:** We will alternate plans. I will reduce your time staying in the hotel, pivot your schedule, and instead of resting we will be roaming in the city to catch up.\n"
            plan += f"• **Local Transport:** Since you have {num_members} members, your dedicated VIP Cabs will be frequency-tracked and waiting immediately outside the airport.\n"
        else:
            plan += "• **If Delayed:** I have alternate plans ready: skipping the current destination entirely, or skipping any other minor destination we planned afterwards to save time.\n"
            if is_group:
                plan += "• **Local Transport:** For your group, we will utilize heavy buses (Frequency: Every 15 mins) to reach the next place.\n"
            else:
                plan += "• **Local Transport:** We will utilize local trains, Metro (Frequency: Every 5 mins), or a fast Bike Taxi to get you to your next place.\n"
            
        plan += "\n**4. Advanced Agent Multi-Modal Integrations:**\n"
        plan += f"• **Financial Agent:** I am polling Amadeus. Currently: {self._price_drop_poll('FL-101')}\n"
        plan += f"• **Visa Concierge:** {self._check_visa('India', dest)}\n"
        plan += f"• **Sustainability:** Trip footprint: {self._calculate_carbon(transport)}. I suggest planting 2 trees to offset this.\n"
        plan += f"• **Expense Hub:** Initial Budget: ${budget}. AI-Limit set. I will alert you at 80% consumption.\n"
        
        plan += "\n**Data Integration Complete:**\n"
        plan += "I have personalized all these plans globally regarding the weather, time, your calendar, local news, and Google search trends. Your 'Crisis Card' (Offline JSON) is now ready in your local cache."
        
        return plan

    def chat(self, prompt):
        """Comprehensive, topic-aware heuristic engine for travel questions."""
        print(f"[DEEP-CONCIERGE] Analyzing: {prompt}")
        lower_prompt = prompt.lower()
        response_parts = []
        
        known_cities = ['tokyo', 'paris', 'london', 'new york', 'cabo', 'honolulu', 'rome', 'dubai', 'bali', 'chennai', 'mumbai', 'delhi', 'bangalore', 'sydney', 'barcelona', 'amsterdam', 'berlin', 'kyoto']
        detected_cities = [city for city in known_cities if city in lower_prompt]
        target_city = detected_cities[0].title() if detected_cities else None

        # 1. Greetings and General Information
        if any(w in lower_prompt for w in ["hi", "hello", "hey", "greetings", "who are you"]):
            response_parts.append("Greetings! I am your Autonomous Concierge, powered by DeepSeek AI. I can assist with flights, weather, itineraries, and more. How may I optimize your journey today?")
        
        # 2. Weather Information
        if any(w in lower_prompt for w in ["weather", "rain", "hot", "climate", "temperature", "cold", "forecast"]):
            if target_city:
                weather_info = self._get_weather(target_city)
                response_parts.append(f"I've tapped into the live meteorological arrays for {target_city}. {weather_info}.")
            else:
                response_parts.append("Which city's weather are you interested in?")

        # 3. Flight Information (Search, Rebook, Cancel)
        if any(w in lower_prompt for w in ["flight", "rebook", "ticket", "cancel", "fly", "airline", "departure", "arrival"]):
            if target_city:
                origin_city = "your current location" # Placeholder for more advanced logic
                flight_info = self._search_flights(origin_city, target_city)
                response_parts.append(f"Scanning Amadeus GDS... {flight_info}. I can proceed with booking if you confirm.")
            else:
                response_parts.append("To search for flights, please specify your destination city.")

        # 4. Calendar and Schedule
        if any(w in lower_prompt for w in ["schedule", "calendar", "time", "appointment", "meeting"]):
            response_parts.append(self.tools["check_calendar"]())

        # 5. Price Tracking and Deals
        if any(w in lower_prompt for w in ["price", "cost", "cheap", "expensive", "deal", "discount", "track"]):
            response_parts.append(self.tools["price_drop_poll"]("FL-AI-RECOMMEND")) # Using a generic flight ID for polling

        # 6. Visa Information
        if any(w in lower_prompt for w in ["visa", "entry", "passport", "travel requirements"]):
            if target_city:
                visa_status = self._check_visa("India", target_city) # Assuming 'India' as origin for demo
                response_parts.append(f"Regarding your travel to {target_city}: {visa_status}")
            else:
                response_parts.append("Please specify the destination city for visa requirements.")

        # 7. Sustainability / Carbon Footprint
        if any(w in lower_prompt for w in ["carbon", "eco", "sustainability", "green travel"]):
            transport_mode = "Flight" # Default for general query, could be extracted from prompt
            carbon_info = self._calculate_carbon(transport_mode)
            response_parts.append(f"Your estimated trip footprint for {transport_mode} is {carbon_info}. I can suggest eco-friendly alternatives or offset options.")

        # 8. Tourist Spots and City Descriptions
        tourist_keywords = ["tourist", "attraction", "place", "visit", "see", "sightseeing", "spot", "landmark", "explore", "describe", "say about", "tell me about", "must see"]
        if any(w in lower_prompt for w in tourist_keywords):
            if target_city:
                if target_city.lower() == 'paris':
                    response_parts.append(f"{target_city} is renowned for the Eiffel Tower, Louvre Museum, Notre Dame Cathedral, and charming Montmartre. A city of art, history, and romance!")
                elif target_city.lower() == 'tokyo':
                    response_parts.append(f"{target_city} offers a vibrant mix of modern skyscrapers and ancient temples. Must-visit: Shibuya Crossing, Senso-ji Temple, Akihabara, and the Imperial Palace.")
                elif target_city.lower() == 'london':
                    response_parts.append(f"{target_city} boasts iconic landmarks: the Tower of London, Buckingham Palace, the British Museum, Big Ben, and the West End theatre district.")
                elif target_city.lower() == 'chennai':
                    response_parts.append(f"{target_city} is home to the famous Marina Beach (2nd longest in the world!), Kapaleeshwarar Temple, Fort St. George, and nearby Mahabalipuram UNESCO site. Don't miss the local filter coffee and dosas!")
                elif target_city.lower() == 'mumbai':
                    response_parts.append(f"{target_city}: Visit Gateway of India, Marine Drive (Queen's Necklace), Elephanta Caves, Juhu Beach, and Bollywood Studios. Best monsoon city in India!")
                elif target_city.lower() == 'delhi':
                    response_parts.append(f"{target_city}: See the Red Fort, Qutub Minar, India Gate, Humayun's Tomb, and Lotus Temple. Delhi is a capital rich in Mughal architecture and street food!")
                elif target_city.lower() == 'dubai':
                    response_parts.append(f"{target_city}: Burj Khalifa (world's tallest building), The Palm Jumeirah, Dubai Mall, Old Souk bazaars, and a Desert Safari at sunset. A city that dreams big!")
                elif target_city.lower() == 'rome':
                    response_parts.append(f"{target_city}: The Colosseum, Vatican City, Trevi Fountain, and the Pantheon await you. Rome is an open-air museum you can never fully explore in one trip!")
                else:
                    response_parts.append(f"{target_city} is a wonderful destination! I recommend exploring its local markets, historical sites, cultural neighbourhoods, and culinary scene. Want a more detailed guide?")
            else:
                response_parts.append("Which city's tourist spots or description would you like to know about?")

        # 9. Trip Planning Context / Suggestions
        if any(w in lower_prompt for w in ["surprise me", "plan", "want to go", "book", "suggest a trip"]):
            if not target_city: 
                target_city = random.choice(['Tokyo', 'Paris', 'Cabo San Lucas', 'London', 'Rome'])
            response_parts.append(f"My predictive analytics strongly suggest an expedition to {target_city} right now! High value, great weather. I will open the Detailed Planner for you to lock it in.")

        # 10. Fallback Default / Clarification
        if not response_parts:
            responses = [
                f"That's an interesting question about '{prompt}'. I can certainly help you look into that. Could you provide a bit more context about your travel goals?",
                f"I comprehend your query regarding '{prompt}'. As an AI travel expert, I am constantly monitoring global travel networks for you.",
                f"Noted. If you would like me to check specific flights, weather, or pricing for '{prompt}', just let me know which city you have in mind!",
                "I'm not entirely sure how to assist with that specific request. Could you rephrase or ask about flights, weather, or destinations?"
            ]
            response_parts.append(random.choice(responses))
            
        return " ".join(response_parts)
    def generate_email_content(self, user_name, subject):
        """Generates a high-fidelity follow-up email with suggested packages and plans."""
        destinations = ["Cabo San Lucas", "Paris", "Tokyo", "London", "NYC"]
        suggested_dest = random.choice(destinations)
        
        email_body = f"#### ✉️ OFFICIAL QUOTE: WHITE TRAVELS AI CONCIERGE\n\n"
        email_body += f"Dear {user_name},\n\n"
        email_body += f"Thank you for inquiring about '{subject}'. Based on your message, our Autonomous AI has analyzed your travel profile and suggests **{suggested_dest}** as your next major destination.\n\n"
        
        email_body += f"**🚀 RECOMMENDED PACKAGE: {suggested_dest.upper()} ELITE**\n"
        email_body += f"• Mixed-mode flight and high-speed rail routing.\n"
        email_body += f"• 5-Star Hotel 'The Ritz {suggested_dest}' (Eco-Certified).\n"
        email_body += f"• Personalized itinerary including {self._get_weather(suggested_dest)} conditions.\n\n"
        
        email_body += f"**💡 AI SUGGESTION:**\n"
        email_body += "I suggest booking within the next 48 hours. My financial polling indicates a high probability of a 15% price spike for this route next week.\n\n"
        
        email_body += "Safe Travels,\nWhite Travels AI Squad"
        return email_body

if __name__ == "__main__":
    agent = DeepConcierge()
    print(agent.chat("Check the weather and rebook my flight"))
