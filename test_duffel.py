import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_duffel_fixed():
    token = os.getenv('DUFFEL_API_TOKEN').replace('Air', '')
    print(f"Testing token: {token}")
    
    url = "https://api.duffel.com/air/offer_requests"
    headers = {
        "Authorization": f"Bearer {token}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json"
    }
    payload = {
        "data": {
            "slices": [{"origin": "LON", "destination": "NYC", "departure_date": "2026-04-15"}],
            "passengers": [{"type": "adult"}]
        }
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"[STATUS] {res.status_code}")
        if res.status_code in [200, 201]:
            print("[SUCCESS] WORKED!")
            return True
        else:
            print(f"[FAIL] {res.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_duffel_fixed()
