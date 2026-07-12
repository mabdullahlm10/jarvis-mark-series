import os
from dotenv import load_dotenv
from groq import Groq

# Load the secret key from .env into the environment
load_dotenv()

# Create the client, handing it the key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Send ONE message to the model
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello and introduce yourself in one sentence."}
    ]
)

# Print what came back
print(response.choices[0].message.content)