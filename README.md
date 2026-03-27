# White Travels

## Description

White Travels is a premium, autonomous agentic travel concierge system. Built with a modern Flask backend and a sleek, minimalist frontend, it leverages real-time hotel data via the RapidAPI Hotels engine to provide a high-end booking experience.

Key features include:
- **Autonomous Hotel Search**: Real-time availability fetching for global destinations.
- **Agentic Infrastructure**: Prepared for LangGraph-powered disruption recovery and "Self-Healing" booking flows.
- **Premium UI**: Modern Dark/Light hybrid theme with minimalist "MMT-style" navigation.
- **Portability**: Fully self-contained with a portable SQLite database and zero-config launcher.

## Getting Started

### Prerequisites
- Python 3.8+
- Active RapidAPI Key (for Hotels API)

### Launching the Application
Simply run the included launcher:
```bash
./run.bat
```
The application will be available at `http://127.0.0.1:5000`.

## Architecture
- **Backend**: Flask / SQLite
- **Styling**: Vanilla CSS (Premium Modern)
- **APIs**: RapidAPI (Hotels4), SMTP (Email Automation)
