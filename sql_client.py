import requests
from config import SD_API_URL, DEFAULT_STEPS, WIDTH, HEIGHT

def generate(prompt: str):
    payload = {
        "prompt": prompt,
        "steps": DEFAULT_STEPS,
        "width": WIDTH,
        "height": HEIGHT,
        "sampler_name": "Euler a"
    }

    r = requests.post(SD_API_URL, json=payload, timeout=3600)
    r.raise_for_status()
    return r.json()
