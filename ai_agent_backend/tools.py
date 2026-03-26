import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Pydantic Models for Data Validation
class FlightData(BaseModel):
    flight_number: str
    airline: str
    status: str
    departure_time: str
    arrival_time: str
    destination: str
    weather_alert: Optional[str] = None

class WeatherData(BaseModel):
    city: str
    temperature: float
    condition: str
    storm_alert: bool
    grounded_duration_hours: int = 0

class CalendarEvent(BaseModel):
    title: str
    start_time: str
    end_time: str
    is_critical: bool = False

# Mock-up Async Tools
async def get_flight_status(pnr: str) -> FlightData:
    """Mock-up for Amadeus/Duffel API"""
    await asyncio.sleep(1)
    # Simulate a disruption UA-402
    return FlightData(
        flight_number="UA-402",
        airline="United Airlines",
        status="CANCELLED",
        departure_time="2026-03-27T14:00:00",
        arrival_time="2026-03-27T16:00:00",
        destination="London (LHR)",
        weather_alert="Severe Storm"
    )

async def get_destination_weather(city: str) -> WeatherData:
    """Mock-up for OpenWeather API"""
    await asyncio.sleep(0.5)
    return WeatherData(
        city=city,
        temperature=12.5,
        condition="Stormy",
        storm_alert=True,
        grounded_duration_hours=24
    )

async def search_flight_alternatives(origin: str, destination: str) -> List[Dict[str, Any]]:
    """Mock-up for Tavily/Exa real-time search"""
    await asyncio.sleep(1.5)
    return [
        {"pathway": "A: Fastest", "flight": "LH-12", "dep": "19:30", "price": "$850", "arrival": "22:00"},
        {"pathway": "B: Comfortable", "flight": "EK-50", "dep": "21:00", "price": "$1200", "arrival": "23:45"},
        {"pathway": "C: The Pivot", "flight": "Tomorrow 09:00", "price": "$600", "arrival": "11:00"}
    ]

async def check_calendar_conflicts(user_id: str) -> List[CalendarEvent]:
    """Mock-up for Google Calendar API"""
    await asyncio.sleep(0.5)
    return [
        CalendarEvent(title="4PM Board Meeting", start_time="2026-03-27T16:00:00", end_time="2026-03-27T17:00:00", is_critical=True)
    ]
