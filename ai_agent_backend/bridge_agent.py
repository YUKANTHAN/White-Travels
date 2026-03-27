import os
from dotenv import load_dotenv
from ai_agent_backend.disruption_graph import travel_agent_app
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv() # Loads your DUFFEL and DEEPSEEK keys 

def check_disaster_status(city):
    """Searches live news for disasters in a specific city."""
    search = TavilySearchResults(max_results=3) # Or use Antigravity's built-in browser tool
    results = search.run(f"current natural disasters or flight cancellations in {city}")
    return results

def run_smart_concierge(user_input, pnr="SIM-ITN-5462"):
    # 1. Ask the existing DeepSeek Agent to analyze the intent 
    # If the user says "My flight is cancelled", detect 'disruption'
    
    if "cancelled" in user_input.lower() or "delay" in user_input.lower():
        print("--- Activating LangGraph Self-Healing Flow ---")
        
        # Ground the logic in actual web-live data
        print("--- Using Browser Agent to check Disasters in NYC ---")
        live_disaster_context = check_disaster_status("New York City")
        
        # 2. Hand off to your LangGraph 
        initial_state = {
            "pnr": pnr,
            "disruption_type": str(live_disaster_context)[:100], # Pass the web results
            "current_status": "analyzing",
            "rebooking_options": []
        }
        
        final_state = travel_agent_app.invoke(initial_state)
        return f"AI Agent Update: Grounded via live search. I've detected a {final_state['disruption_type']} issue. Status: {final_state['current_status']}"
    
    return "How can I help with your premium travel plans today?"

# Test execution
if __name__ == "__main__":
    print(run_smart_concierge("My flight is cancelled because of the storm!"))
