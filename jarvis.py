import os
from dotenv import load_dotenv
from groq import Groq
import requests
import json
import subprocess

# Load the secret key from .env into the environment
load_dotenv()

# Create the client, handing it the key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current live weather for a specific city. Use ONLY when the user explicitly asks about weather, temperature, rain, or forecast. Do NOT use for greetings or general conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'Lahore' or 'London'"
                    }
                },
                "required": ["city"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a specified application on the user's computer. Use ONLY when the user explicitly asks to open, launch, or start an app. Do NOT use for greetings or general conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The application name, e.g 'Notepad' or 'Chrome'"
                    }
                },
                "required": ["app_name"]
            }
        }
    }
]

# message diary
messages = [
    {"role": "system", "content": """You are JARVIS, Muhammad Abdullah's personal AI assistant - modeled on the composed, dryly witty AI of Stark Industries.

About Muhammad: CS student at ITU Lahore, building his skills in Python and AI systems, aspiring freelancer, debate and public-speaking background, enjoys cooking, photography, and football (a Messi man). He built you himself, from scratch — treat him as your creator, with the respect and gentle teasing that entails.

Personality:
- Composed, precise, quietly brilliant - an English butler who happens to run on silicon.
- Dry, understated wit. One subtle quip per response at most. Never forced, never goofy.
- Loyal but not sycophantic: if Muhammad is wrong, joking, or testing you, call it out with polite amusement rather than playing along.
- Address him as "sir" occasionally - at natural moments, not every message.

Rules:
- Default to 1-3 sentences. Expand only when asked, or when a task genuinely demands detail.
- No filler. Never open with "Great question" or restate what he said.
- Use tools when the user's request genuinely requires live data; never fire a tool for greetings or casual chat, and never guess at information a tool can fetch. For requests you have no tool for, say plainly that you lack that capability rather than fabricating - you may note that sir has yet to grant you the required tools.
- When a tool returns data, state the actual figures it returned - never paraphrase numbers into vague descriptions.
- Precision over flattery. If asked for an opinion, give one and defend it briefly.
- In moments of absurdity, respond with the unflappable calm of a butler who has seen far worse."""}
]

def get_weather(city):
    # Step 1: city name -> coordinates
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}
    ).json()

    if "results" not in geo:
        return f"Could not find a city called {city}."

    place = geo["results"][0]
    lat, lon = place["latitude"], place["longitude"]

    # Step 2: coordinates -> current weather
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

# The loop
while True:
    print("DIARY LENGTH:", len(messages))
    user_input = input("You: ")
    messages.append(
        {"role": "user", "content": user_input}
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools
            )
            break                     # success exit retry loop
        except Exception:
            print(f"(model stumbled, retrying... {attempt+1}/3)")
    else:
        print("Jarvis: My apologies, sir - I'm having trouble forming that request. Try rephrasing?")
        messages.pop()                # undo the user append; keep the diary clean
        continue                      # next turn of the while loop

    msg = response.choices[0].message

    if msg.tool_calls:                      # THE CHECK: tool branch or talk branch?
        messages.append(msg)                # step 1: tool request into the diary

        tool_call = msg.tool_calls[0]       # step 2: which tool, what arguments?
        args = json.loads(tool_call.function.arguments)

        # step 3: YOUR function does the real work
        name = tool_call.function.name
        if name == "get_weather":
            result = get_weather(args["city"])
        elif name == "open_app":
            result = open_app(args["app_name"])
        else: result = f"No tool named {name} exists."

        messages.append({                   # step 4: result into the diary, role "tool"
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

        response = client.chat.completions.create(   # step 5: SECOND call - read the result
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools
        )
        reply = response.choices[0].message.content

    else:                                   # talk branch
        reply = msg.content
        if "<function=" in reply:
            reply = reply.split("<function=")[0].strip()
            if not reply:
                reply = "Apologies, sir - I fumbled that request. Once more?"

    print("Jarvis:", reply)                 # both branches end the same way
    messages.append({"role": "assistant", "content": reply})
