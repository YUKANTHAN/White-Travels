from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Define the "State" (The memory your agent passes around)
class AgentState(TypedDict):
    pnr: str
    disruption_type: str  # e.g., "climate" or "company"
    current_status: str
    rebooking_options: list
    # 1. Define your Nodes (The functions the AI will run)
def check_weather(state: AgentState):
    # Logic to use your ddgs/OpenWeather API goes here
    return {"disruption_type": "climate"}

def propose_rebooking(state: AgentState):
    # Logic to ask Gemma 3 for alternatives based on the disruption
    return {"current_status": "rebooked"}

# 2. Build the Graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("detect_issue", check_weather)
workflow.add_node("rebook", propose_rebooking)

# 3. Connect the Edges (The flow)
workflow.add_edge(START, "detect_issue")
workflow.add_edge("detect_issue", "rebook")
workflow.add_edge("rebook", END)

# 4. Compile it into an active application
travel_agent_app = workflow.compile()