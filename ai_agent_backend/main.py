from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .graph import app_graph

app = FastAPI(title="White Travels Disruption Command Center")

class BookingRequest(BaseModel):
    pnr: str
    user_id: str

@app.get("/")
async def root():
    return {"message": "Autonomous Agentic Travel Concierge API is Online"}

@app.post("/analyze-disruption")
async def analyze_disruption(request: BookingRequest):
    """
    Triggers the LangGraph agent to:
    1. Monitor PNR
    2. Check Weather/Search alternatives
    3. Check Calendar Conflicts
    4. Generate 3 Pathways
    """
    initial_state = {
        "pnr": request.pnr,
        "user_id": request.user_id,
        "flight_data": {},
        "weather_impact": {},
        "calendar_conflicts": [],
        "pathways": [],
        "status": "STARTING",
        "next_node": "monitor"
    }
    
    try:
        final_state = await app_graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirm-rebooking")
async def confirm_rebooking(user_id: str, pathway_id: str):
    """
    Human-in-the-loop breakpoint confirmation point.
    In production, this would persist the chosen pathway to Supabase/Flight API.
    """
    return {"status": "SUCCESS", "message": f"Confirmed Pathway {pathway_id} for user {user_id}"}

# Run with: uvicorn main:app --reload
