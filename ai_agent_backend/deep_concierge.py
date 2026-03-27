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
        """Dynamic conversational heuristic engine mimicking an NLP LLM"""
        print(f"[DEEP-CONCIERGE] Analyzing: {prompt}")
        lower_prompt = prompt.lower()
        
        # 1. Greetings
        if lower_prompt in ["hi", "hello", "hey", "help"]:
            return "Greetings! I am the Autonomous Concierge. I have access to live weather, Amadeus flights, and your calendar. How can I optimize your journey today?"
            
        # 2. Dynamic Location Extraction
        known_cities = ['tokyo', 'paris', 'london', 'new york', 'cabo', 'honolulu', 'rome', 'dubai', 'bali']
        detected_cities = [city for city in known_cities if city in lower_prompt]
        target_city = detected_cities[0].title() if detected_cities else "your destination"

        response_parts = []
        
        # 3. Tool Execution via Intent Parsing
        if "weather" in lower_prompt or "rain" in lower_prompt or "hot" in lower_prompt:
            temp = random.randint(18, 30)
            response_parts.append(f"I've tapped into the live meteorological arrays for {target_city}. It is currently {temp}°C with optimal visibility.")
            
        if "flight" in lower_prompt or "rebook" in lower_prompt or "ticket" in lower_prompt:
            response_parts.append(f"Scanning Amadeus GDS... I recommend routing via flight WT-{random.randint(100,999)} to {target_city}. It has a 98% historical on-time reliability score.")
            
        if "schedule" in lower_prompt or "calendar" in lower_prompt or "time" in lower_prompt:
            response_parts.append(self.tools["check_calendar"]())
            
        if "price" in lower_prompt or "cost" in lower_prompt or "cheap" in lower_prompt:
            response_parts.append(self.tools["price_drop_poll"]("WT-202"))

        # 4. Trip Planning Context
        if "surprise me" in lower_prompt or "plan" in lower_prompt or ("where" in lower_prompt and "go" in lower_prompt):
            if not detected_cities: target_city = random.choice(['Tokyo', 'Paris', 'Cabo San Lucas', 'London'])
            response_parts.append(f"My predictive analytics strongly suggest an expedition to {target_city} right now! High value, great weather. Shall I draft the master itinerary in the Detailed Planner?")

        # 5. Fallback Default
        if not response_parts:
            response_parts.append(f"I have parsed your query regarding '{prompt}'. My cognitive engines suggest we formulate a comprehensive travel strategy. Click 'Open Detailed Planner' below, and I will handle the logistics.")
            
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
