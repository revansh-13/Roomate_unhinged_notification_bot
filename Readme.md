# HomeOps-9000: Automated Passive-Aggressive Roommate Bot

An IoT-powered domestic compliance system. When roommates leave unwashed dishes or clutter in communal areas, ultrasonic echolocation alerts an ESP32, tunnels over HTTPS to a local FastAPI server, and prompts an LLM to generate deadpan, escalating public address announcements read aloud via neural TTS.

## Architecture
- **Edge Sensor:** ESP32 + HC-SR04 Ultrasonic Sensor
- **Backend:** FastAPI + Uvicorn
- **Tunneling:** Ngrok / Pyngrok
- **Intelligence:** Google GenAI (Gemini 2.5 Flash)
- **Audio Pipeline:** Edge-TTS + Pygame Mixer

## Setup
1. Clone this repository: