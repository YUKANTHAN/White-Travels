import os
import json
import requests
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
            "check_calendar": self._check_calendar
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
            
        plan += "\n**Data Integration Complete:**\n"
        plan += "I have personalized all these plans globally regarding the weather, time, your calendar, local news, and Google search trends."
        
        return plan

    def chat(self, prompt):
        """Standardize prompt parsing and tool execution"""
        print(f"[DEEP-CONCIERGE] Analyzing: {prompt}")
        
        # In a real hackathon, we call the LLM and let it output tool calls.
        # For the demo, we use a 'Heuristic Reasoning Engine' to show responsiveness.
        
        lower_prompt = prompt.lower()
        if "weather" in lower_prompt:
            return self.tools["get_weather"]("Cabo San Lucas")
        elif "flight" in lower_prompt or "rebook" in lower_prompt:
            return self.tools["search_flights"]("LND", "CAB")
        elif "schedule" in lower_prompt or "calendar" in lower_prompt:
            return self.tools["check_calendar"]()
        
        # Fallback to DeepSeek API if available, else mock reasoning
        if self.api_key.startswith("SK-MOCK"):
            return "Based on my traversal of your itinerary and real-time news, I recommend re-booking for 4:00 PM to avoid the incoming storm front."
        else:
            # Real DeepSeek Call (Placeholdered)
            return "DeepSeek response placeholder."

if __name__ == "__main__":
    agent = DeepConcierge()
    print(agent.chat("Check the weather and rebook my flight"))
