import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
import subprocess
import asyncio
import datetime
import pyaudio

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_weather(city):
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}
    ).json()
    if "results" not in geo:
        return f"Could not find a city called {city}."
    place = geo["results"][0]
    lat, lon = place["latitude"], place["longitude"]
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True}
    ).json()
    current = weather["current_weather"]
    return f"{place['name']}: {current['temperature']}°C, wind {current['windspeed']} km/h"

def open_app(app_name):
    try:
        subprocess.Popen([app_name])
        return f"Opened {app_name}."
    except FileNotFoundError:
        return f"Could not find an application called {app_name}."

tool_declarations = types.Tool(function_declarations=[
    {
        "name": "get_weather",
        "description": "Get the current live weather for a specific city. Use ONLY when the user explicitly asks about weather, temperature, rain, or forecast. Do NOT use for greetings or general conversation.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Lahore' or 'London'"}
            },
            "required": ["city"]
        }
    },
    {
        "name": "open_app",
        "description": "Open a specified application on the user's computer. Use ONLY when the user explicitly asks to open, launch, or start an app. Do NOT use for greetings or general conversation.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "The application name, e.g. 'Notepad' or 'Chrome'"}
            },
            "required": ["app_name"]
        }
    }
])

try:
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    raise SystemExit(
        "system_prompt.txt not found. Copy system_prompt.example.txt to "
        "system_prompt.txt and fill in your details."
    )

live_config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=SYSTEM_PROMPT,
    tools=[tool_declarations],
    input_audio_transcription={},
    output_audio_transcription={},
)

LOG_FILE = "conversation_log.txt"

def log_turn(label, text):
    text = text.strip()
    if not text:
        return
    timestamp = datetime.datetime.now().strftime("%H:%M")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {label}: {text}\n")

CHUNK = 512

async def send_audio(session, mic):
    while True:
        data = await asyncio.to_thread(mic.read, CHUNK, exception_on_overflow=False)
        await session.send_realtime_input(
            audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
        )

async def receive_audio(session, speaker):
    user_buffer = ""
    jarvis_buffer = ""
    while True:
        async for response in session.receive():
            if response.data:
                await asyncio.to_thread(speaker.write, response.data)

            if response.server_content:
                sc = response.server_content

                if sc.input_transcription and sc.input_transcription.text:
                    user_buffer += sc.input_transcription.text
                if sc.input_transcription and sc.input_transcription.finished:
                    log_turn("You", user_buffer)
                    user_buffer = ""

                if sc.output_transcription and sc.output_transcription.text:
                    if user_buffer:
                        log_turn("You", user_buffer)
                        user_buffer = ""
                    jarvis_buffer += sc.output_transcription.text
                if sc.output_transcription and sc.output_transcription.finished:
                    log_turn("Jarvis", jarvis_buffer)
                    jarvis_buffer = ""

                if sc.turn_complete and jarvis_buffer:
                    log_turn("Jarvis", jarvis_buffer)
                    jarvis_buffer = ""

            if response.tool_call:
                function_responses = []
                for fc in response.tool_call.function_calls:
                    print(f"[tool requested: {fc.name}({fc.args})]")
                    if fc.name == "get_weather":
                        result = get_weather(fc.args["city"])
                    elif fc.name == "open_app":
                        result = open_app(fc.args["app_name"])
                    else:
                        result = f"No tool named {fc.name} exists."

                    function_responses.append(types.FunctionResponse(
                        id=fc.id,
                        name=fc.name,
                        response={"result": result}
                    ))
                await session.send_tool_response(function_responses=function_responses)

async def main():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== Session started {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    p = pyaudio.PyAudio()
    mic = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                 input=True, frames_per_buffer=CHUNK)
    speaker = p.open(format=pyaudio.paInt16, channels=1, rate=24000,
                     output=True)

    async with client.aio.live.connect(
        model="gemini-3.1-flash-live-preview",
        config=live_config
    ) as session:
        print("JARVIS online. Speak. (Ctrl+C to end)")
        async with asyncio.TaskGroup() as tg:
            tg.create_task(send_audio(session, mic))
            tg.create_task(receive_audio(session, speaker))

asyncio.run(main())
