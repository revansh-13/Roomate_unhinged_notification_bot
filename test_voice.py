import asyncio
import os
import edge_tts
import pygame

# Initialize pygame mixer for sound playback
pygame.mixer.init()

async def speak(text):
    voice = "en-US-ChristopherNeural"  # Authoritative, calm narrator voice
    output_file = "test.mp3"
    
    print("Generating voice audio...")
    comm = edge_tts.Communicate(text, voice)
    await comm.save(output_file)

    print("Playing announcement...")
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    
    # Wait until the sound finishes playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    pygame.mixer.music.unload()
    if os.path.exists(output_file):
        os.remove(output_file)
    print("Done!")

if __name__ == "__main__":
    test_message = "HomeOps unit online. Passive aggressive protocol initialized."
    asyncio.run(speak(test_message))