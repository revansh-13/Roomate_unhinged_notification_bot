import asyncio
import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import edge_tts
import pygame
import uvicorn
from pyngrok import ngrok
from google import genai

app = FastAPI()
pygame.mixer.init()

# Setup Gemini Client
api_key = os.environ.get("GEMINI_API_KEY", "PASTE_KEY_HERE_IF_NOT_SET_IN_ENV")
ai_client = genai.Client(api_key=api_key)

class SensorPing(BaseModel):
    location: str
    distance_cm: float

# Strike counter to escalate tone
strike_count = 0

async def generate_roast(location: str, distance_cm: float, strikes: int) -> str:
    prompt = f"""
You are 'HomeOps-9000', an emotionless, deadpan, passive-aggressive corporate AI system overseeing an apartment.
An ultrasonic sensor detected dirty dishes or junk cluttering the {location}.
Clearance distance to the mess is {distance_cm:.1f} cm.
This is consecutive strike #{strikes} without the mess being resolved.

Rules:
1. Deliver a formal PA announcement.
2. Be subtly sarcastic, disappointed, and dry.
3. Keep it strictly under 2 sentences.
4. Do NOT include markdown, asterisks, brackets, or stage directions. Only speakable plain text.
"""
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"[LLM Error]: {e}")
        return f"Attention residents. Unauthorized crockery detected in the {location}. Clearance is down to {distance_cm:.1f} centimeters. Clear it immediately."

async def play_audio_async(text: str):
    output_file = "announcement.mp3"
    voice = "en-US-ChristopherNeural"
    
    communicate = edge_tts.Communicate(text, voice, rate="+5%")
    await communicate.save(output_file)

    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    if os.path.exists(output_file):
        os.remove(output_file)

async def handle_alert_pipeline(location: str, distance_cm: float, strike: int):
    # 1. Generate text
    print(f"\n[AI THINKING] Drafting announcement for Strike #{strike}...")
    script = await generate_roast(location, distance_cm, strike)
    print(f"[AI SCRIPT]: \"{script}\"")
    
    # 2. Play audio
    await play_audio_async(script)

@app.post("/api/sensor-alert")
async def receive_sensor_alert(data: SensorPing, background_tasks: BackgroundTasks):
    global strike_count
    strike_count += 1
    
    print(f"\n[PING RECEIVED] {data.location} | Distance: {data.distance_cm:.1f} cm (Strike #{strike_count})")
    
    # Run audio & LLM generation in background so ESP32 gets an instant 200 OK response
    background_tasks.add_task(handle_alert_pipeline, data.location, data.distance_cm, strike_count)
    
    return {"status": "queued", "strike": strike_count}

if __name__ == "__main__":
    tunnel = ngrok.connect(8000)
    public_url = tunnel.public_url

    print("\n" + "=" * 60)
    print("LIVE TUNNEL URL:")
    print(f"{public_url}/api/sensor-alert")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)