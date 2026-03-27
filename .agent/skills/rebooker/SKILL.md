---
name: rebooker
description: Detects flight/train cancellations in bookings.json and rebooks passengers via Amadeus/Mock SDK.
---

# Rebooker Skill
Handle autonomous recovery for travel disruptions.

## Logic Flow
1. **Monitor**: Watch `bookings.json` for status updates.
2. **Detect**: If `status == "CANCELLED"`, trigger `disruption_engine.py`.
3. **Analyze**: Call `check_status()` to verify with real-time (mocked) data.
4. **Rebook**: Call `get_best_alternative()` to find optimal path.
5. **Report**: Present findings as a **Walkthrough Artifact**.

## Scripts
- `disruption_engine.py`: Core logic for API calls.

## Usage
Activate whenever a disruption alert is clicked or a batch check is requested.
