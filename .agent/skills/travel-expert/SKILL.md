---
name: travel-expert
description: Monitors itinerary.json for flight cancellations and rebooks via Amadeus.
---

# Travel Expert Skill
High-intelligence autonomous rebooking for flight disruptions.

## Core Logic
1. **Monitor**: Watch `itinerary.json` in root.
2. **Detect**: Trigger if `status == "CANCELLED"`.
3. **Execute**: Run `scripts/rebook_logic.py`.
4. **Update**: Final status should be `REBOOKED`.
5. **Output**: Result shown as a **Walkthrough Artifact**.

## Usage
Activate whenever `itinerary.json` is modified.
