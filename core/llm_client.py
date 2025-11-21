import requests
import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY not found. Check your .env file.")

MODEL = "models/gemini-2.0-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

def call_llm(system_prompt, user_prompt):
    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}

    text_prompt = f"System:\n{system_prompt}\n\nUser:\n{user_prompt}"

    body = {
        "contents": [
            {
                "parts": [{"text": text_prompt}]
            }
        ]
    }

    res = requests.post(ENDPOINT, params=params, headers=headers, json=body)

    if res.status_code != 200:
        raise RuntimeError(f"Gemini API error {res.status_code}: {res.text}")

    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
