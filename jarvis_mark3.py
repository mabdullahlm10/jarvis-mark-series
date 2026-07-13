import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
import json
import subprocess
from elevenlabs.client import ElevenLabs

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


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

def speak(text):
    audio = el_client.text_to_speech.convert(
        text=text,
        voice_id="onwK4e9ZLuTAKqWW03F9",
        model_id="eleven_multilingual_v2"
    )
    with open("reply.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)
    os.startfile("reply.mp3")

# ---- tools: SAME schema idea, Gemini's wrapper ----
# CHANGED: bare dicts (no {"type":"function"} outer layer), wrapped in types.Tool
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

# CHANGED: system prompt is NOT diary index 0 anymore — it rides in the config
try:
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    raise SystemExit(
        "system_prompt.txt not found. Copy system_prompt.example.txt to "
        "system_prompt.txt and fill in your details."
    )

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[tool_declarations]
)

# the diary — starts EMPTY now (system prompt lives in config)
history = []

while True:
    print("DIARY LENGTH:", len(history))
    user_input = input("You: ")

    # CHANGED: Gemini's message format — "parts" instead of "content",
    # and the model's role is called "model", not "assistant"
    history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",          # CHANGED: the brain
                contents=history,                   # the diary, same idea
                config=config
            )
            break
        except Exception as e:
            print(f"(model stumbled, retrying... {attempt+1}/3) — {e}")
    else:
        print("Jarvis: My apologies, sir - trouble forming that request. Once more?")
        history.pop()
        continue

    # CHANGED: where the tool request lives - response.function_calls
    if response.function_calls:
        history.append(response.candidates[0].content)   # tool request into diary

        fc = response.function_calls[0]
        name = fc.name
        args = fc.args                # ALREADY a dict - no json.loads needed!

        if name == "get_weather":
            result = get_weather(args["city"])
        elif name == "open_app":
            result = open_app(args["app_name"])
        else:
            result = f"No tool named {name} exists."

        # tool result into the diary - Gemini's version of role:"tool"
        history.append(types.Content(
            role="user",
            parts=[types.Part.from_function_response(name=name, response={"result": result})]
        ))

        # SECOND call
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=history,
                    config=config
                )
                break
            except Exception as e:
                print(f"(model stumbled, retrying... {attempt+1}/3) — {e}")
        else:
            print("Jarvis: Apologies, sir - I fetched the data but tripped narrating it.")
            continue

        reply = response.text
    else:
        reply = response.text

    print("Jarvis:", reply)
    speak(reply)
    history.append(types.Content(role="model", parts=[types.Part(text=reply)]))