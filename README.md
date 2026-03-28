# White Travels

## Overview

White Travels is an innovative, AI-driven autonomous travel concierge designed to elevate the traditional booking experience into a proactive, frictionless "super-app." Built with a robust Python and Flask backend coupled with a premium, dynamic web interface, the platform serves as a modern travel companion that prioritizes user peace of mind.

At its core, White Travels moves beyond standard reactive ticketing. It features specialized AI agents that continuously monitor active itineraries:
- **Travel Expert**: Monitors user itineraries and handles seamless interactions.
- **Rebooker**: Detects cancellations and manages one-click automated rebooking options through services like Amadeus and Duffel.
- **Real-Time Disaster Specialist**: Continuously tracks real-world variables globally, alerting users to natural disasters and automating swift recovery workflows for safe travel.

Additionally, the suite supports complex group coordination with multi-passenger itineraries, automated conversational workflows that send personalized travel packages, and a persistent AI chatbox for immediate user engagement. 

## Features

- **Autonomous Agent Workflows**: Integration with n8n for continuous, real-time disruption monitoring.
- **Instant Rebooking**: One-click recovery from disruptions via Amadeus and Duffel APIs.
- **Real-Time Natural Disaster Monitoring**: Proactive notifications and contingency planning.
- **Premium UI & Dynamic Design**: Modern Dark/Light mode theme with minimalist layouts and micro-animations for an elevated user experience.
- **Multimodal Support**: Manage flights, trains, and custom travel packages simultaneously.
- **Automated Communication**: Twilio integration for instant SMS and email alerting during disruptions.

## Technologies Used

- **Backend**: Python 3.8+, Flask, MongoDB / SQLite
- **Automation / Orchestration**: n8n, custom watcher scripts
- **External Integration**: Amadeus SDK, Duffel API, Twilio, PyWhatKit
- **Frontend**: Vanilla HTML/CSS with JS (Responsive and animated "MMT-styled" premium view)

## Getting Started

### Prerequisites
- Python 3.8 or higher.
- API Keys for Amadeus, Duffel, and Twilio.
- Active n8n environment if deploying automated workflows.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YUKANTHAN/White-Travels.git
   cd White-Travels
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` and configure your API keys.

4. **Launch the platform:**
   Simply run the included launcher:
   ```bash
   ./run.cmd
   ```
   The application will be available at `http://127.0.0.1:5000`.

## Architecture

- **Backend API (`flask_app/`)**: Handles core logic, routing, and user interface.
- **AI Agent Backend (`ai_agent_backend/`)**: Contains Deep Concierge intelligence and integration logic.
- **Agent Skills (`.agent/`)**: Pre-programmed autonomous agents (Travel Expert, Rebooker, Real-Time Disaster Specialist).
- **Automation Templates**: Pre-configured JSON templates (`n8n_disruption_agent.json`, `n8n_real_time_detector.json`) for seamless integration.

## License
Yukanthan P G
Vignesh B
RamKumar J
Ramakrishnan M
