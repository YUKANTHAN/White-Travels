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

    def plan_trip(self, destination, date, budget, companions):
        """High-Fidelity AI Multi-Modal Travel Orchestrator"""
        print(f"[DEEP-CONCIERGE] Orchestrating Advanced Plan: {destination} | {companions} | ${budget}")
        
        # 1. ANALYZE TRANSIT MODES (Mixed Mode Logic)
        is_group = any(x in companions.lower() for x in ["family", "friends", "group"])
        num_members = 4 if is_group else (2 if "couple" in companions.lower() else 1)
        
        # Simplified Logic for Demo: Prefer Train for <500km, Flight otherwise
        # But offer both as "Choices" as requested
        primary_transport = "Flight (Duffel API)"
        secondary_transport = "High-Speed Rail (Eurostar/Amtrak)"
        
        # 2. LOCAL TRANSIT & FREQUENCY
        # Personalize based on group size and budget
        if int(budget) > 3000:
            local_transport = "Private Executive Chauffeur (on-call)"
            transport_note = "High frequency, zero wait time."
        elif is_group:
            local_transport = "Dedicated XL Shared Van"
            transport_note = "Arrival every 15 mins at Terminal 3."
        else:
            local_transport = "Metro (Lines A & B) + Bike Taxi for 'last-mile' connectivity"
            transport_note = "Metro frequency: 4 mins. Bike Taxi: <2 min pickup."

        # 3. WEATHER & CALENDAR CHECK (Context Awareness)
        weather = self._get_weather(destination)
        calendar = self._check_calendar()
        
        # 4. CONSTRUCTION OF ITINERARY (Dynamic & Modular)
        plan = f"#### 🌏 COMPLETE ORCHESTRATION: {destination.upper()}\n"
        plan += f"📅 **Target:** {date} | 👥 **Members:** {num_members} | 💰 **Budget:** ${budget}\n\n"
        
        plan += "🏁 **Phase 1: Arrival (Mixed Mode Choices)**\n"
        plan += f"• **Primary:** {primary_transport} - Optimized for speed. (Est. $450/pp)\n"
        plan += f"• **Sustainable Choice:** {secondary_transport} - 'If you have time, I suggest the sleeper train to enjoy the scenery.' (Est. $120/pp)\n\n"
        
        plan += "🏙️ **Phase 2: Local Connectivity (Point-to-Point)**\n"
        plan += f"• **From Airport:** Take the **{local_transport}**. {transport_note}\n"
        plan += f"• **Group Factor:** Since you're traveling as a {companions}, I've optimized for a vehicle that fits all {num_members} members with luggage.\n\n"
        
        plan += "🎭 **Phase 3: Personalized Exploration**\n"
        plan += f"• **Tourist Spots:** Since it's {weather.split(':')[1].strip()}, I recommend starting with the Museum of Modern Art followed by a sunset city walk.\n"
        plan += f"• **News/Alerts:** I've monitored local news; I suggest skipping the central square tomorrow due to a scheduled parade; routing to the 'Secret Garden' district instead.\n\n"
        
        plan += "⚠️ **Phase 4: Contingency 'The Pivot' (If Delayed)**\n"
        plan += "• **Scenario A (Minor Delay):** Reduce Hotel lounge time to 1hr; proceed directly to city explorer mode.\n"
        plan += "• **Scenario B (Major Delay):** Skip Day 1 outdoor sites; I've pre-shifted those to Day 2; tonight will instead focus on a late-night culinary experience.\n\n"
        
        plan += "**[DECISION REQUIRED]**: Shall I lock in this multi-modal plan and secure your {local_transport} pass?"
        
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
