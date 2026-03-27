from typing import List, Dict, Any, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from .tools import get_flight_status, get_destination_weather, search_flight_alternatives, check_calendar_conflicts
import operator

# Define State Schema
class AgentState(TypedDict):
    pnr: str
    user_id: str
    flight_data: Dict[str, Any]
    weather_impact: Dict[str, Any]
    calendar_conflicts: List[Dict[str, Any]]
    pathways: List[Dict[str, Any]]
    status: str
    next_node: str

# Node Definitions
async def monitor_node(state: AgentState):
    """STEP 1: Identify disruption severity"""
    flight = await get_flight_status(state['pnr'])
    return {
        "flight_data": flight.dict(),
        "status": "ANALYZING" if flight.status != "ON_TIME" else "MONITORING",
        "next_node": "researcher" if flight.status != "ON_TIME" else END
    }

async def researcher_node(state: AgentState):
    """STEP 3: Verify weather and find alternatives"""
    destination = state['flight_data']['destination']
    weather = await get_destination_weather(destination)
    alternatives = await search_flight_alternatives("CurrentLoc", destination)
    
    return {
        "weather_impact": weather.dict(),
        "pathways": alternatives,
        "next_node": "secretary"
    }

async def secretary_node(state: AgentState):
    """STEP 2: Scan for conflicts and combine intelligence"""
    conflicts = await check_calendar_conflicts(state['user_id'])
    return {
        "calendar_conflicts": [c.dict() for c in conflicts],
        "next_node": "messenger"
    }

async def messenger_node(state: AgentState):
    """STEP 4: Format final response for Human-in-the-Loop"""
    # Logic to construct the high-agency message
    return {
        "status": "WAITING_FOR_USER",
        "next_node": END
    }

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("monitor", monitor_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("secretary", secretary_node)
workflow.add_node("messenger", messenger_node)

workflow.set_entry_point("monitor")

workflow.add_conditional_edges(
    "monitor",
    lambda x: x["next_node"],
    {
        "researcher": "researcher",
        END: END
    }
)

workflow.add_edge("researcher", "secretary")
workflow.add_edge("secretary", "messenger")
workflow.add_edge("messenger", END)

app_graph = workflow.compile()
