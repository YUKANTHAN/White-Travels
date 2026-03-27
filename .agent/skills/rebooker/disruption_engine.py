import json
import random

# Minimal Disruption Engine
def check_status(id: str):
    """Verifies disruption status. In production, calls Amadeus/Duffel."""
    # Simulation: 70% chance of being verified disruption
    return random.random() < 0.7

def get_best_alternative(disrupted_id: str):
    """Finds best flight/train alternative based on destination."""
    alternatives = [
        {"id": "LH-12", "type": "Flight", "name": "Lufthansa Express", "time": "19:30", "price": "+$120"},
        {"id": "TR-99", "type": "Train", "name": "Grand Euro Express", "time": "21:15", "price": "-$40"},
        {"id": "ST-08", "type": "Stay", "name": "Marriott Luxury Day Stay", "time": "Anytime", "price": "$0 (Voucher)"}
    ]
    return random.choice(alternatives)

if __name__ == "__main__":
    import sys
    # Example execution: python disruption_engine.py FL202
    target = sys.argv[1] if len(sys.argv) > 1 else "FL202"
    if check_status(target):
        print(json.dumps({"status": "CANCELLED", "target": target, "alternative": get_best_alternative(target)}))
    else:
        print(json.dumps({"status": "SAFE", "target": target}))
