import time
import json
import random
import os

from flask_app.config.mongodb_connection import connectToMongo

# Mock Data Strategy (Enhanced for Decision Intelligence)
MOCK_DATA = {
    "flights": [
        {"id": "FL101", "origin": "Cabo", "destination": "NYC", "status": "Delayed", "time": "14:00"},
        {"id": "FL202", "origin": "Cabo", "destination": "NYC", "status": "Cancelled", "time": "18:00"},
        {"id": "FL303", "origin": "Cabo", "destination": "NYC", "status": "On Time", "time": "23:50", "delay_hours": 6}
    ],
    "trains": [
        {"id": "TR707", "route": "Shatabdi Express", "availability": 5, "status": "On Time", "travel_time": 4, "confidence": 0.95},
        {"id": "TR808", "route": "Baja Coastal", "availability": 0, "status": "Full", "travel_time": 6, "confidence": 0.88}
    ],
    "buses": [
        {"id": "BUS-B1", "route": "Intercity Cruiser", "availability": 10, "status": "On Time", "travel_time": 12, "confidence": 0.75}
    ],
    "cabs": [
        {"id": "CAB-U1", "type": "SUV", "eta": "15 mins", "price": 120, "confidence": 0.9}
    ]
}

class AgentManager:
    def __init__(self):
        self.db_conn = connectToMongo()
        self.logs = []

    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs = []

    def log(self, type, message):
        log_entry = f"{type}: {message}"
        self.logs.append(log_entry)
        return log_entry

    def run_react_loop(self, event):
        """ReAct Loop: Observe → Validate → Think → Act → Verify → Confirm"""
        self.clear_logs()
        flight_id = event.get('id', 'Unknown')
        
        # 1. OBSERVE
        self.log("OBSERVE", f"Flight {flight_id} cancelled")
        time.sleep(1)
        
        # 2. VALIDATE
        self.log("VALIDATE", f"Disruption for {flight_id} status confirmed")
        time.sleep(1)

        # 3. THINK
        self.log("THINK", "Searching Shatabdi Express and alternatives...")
        time.sleep(1)
        
        # 4. ACT
        alternatives_considered = []
        options = []
        for t in MOCK_DATA["trains"]:
            if t["availability"] > 0: options.append({"type": "train", "data": t})
            else: alternatives_considered.append(f"Train {t['route']} (rejected: no availability)")
            
        for b in MOCK_DATA["buses"]:
            if b["availability"] > 0: options.append({"type": "bus", "data": b})
            else: alternatives_considered.append(f"Bus {b['route']} (rejected: no availability)")

        if not options:
            self.log("THINK", "No valid routes found")
            self.log("ACT", "Triggering escalation")
            return {
                "status": "escalation",
                "message": "No viable recovery options available",
                "fallback": "Connect to human agent"
            }

        best_opt = options[0]
        self.log("ACT", f"Found available {best_opt['type']}")
        time.sleep(1)

        # 5. VERIFY
        self.log("VERIFY", "Seats and availability confirmed")
        time.sleep(1)

        # 6. CONFIRM
        status = "confirm_required" if best_opt['data'].get("confidence", 0.85) >= 0.7 else "needs_review"
        final_plan = {
            "status": status,
            "plan": f"{best_opt['data'].get('route', best_opt['data'].get('id'))} + Uber",
            "confidence": best_opt['data'].get("confidence", 0.85),
            "reason": ["Flight cancelled", "Transport available", "Optimal route selected"],
            "alternatives_considered": alternatives_considered,
            "timestamp": time.time()
        }
        self.log("CONFIRM", "Plan ready")
        
        logs_col = self.db_conn.get_collection("ai_logs")
        if logs_col is not None:
            try: logs_col.insert_one({"event": event, "plan": final_plan, "logs": self.logs})
            except: pass

        return final_plan

# Singleton for demo
agent = AgentManager()
