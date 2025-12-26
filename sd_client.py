import requests
from config import SD_API_URL

def generate(prompt):
    payload = {
        "prompt": prompt,
        "negative_prompt": "blurry, low quality, bad anatomy, bad hands",
        "steps": 25,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7.5,
        "width": 512,
        "height": 512,
        "seed": -1,
        "batch_size": 1,
        "n_iter": 1,
        "restore_faces": False,
        "tiling": False,
        "enable_hr": False
    }

    r = requests.post(SD_API_URL, json=payload, timeout=3600)
    r.raise_for_status()
    return r.json()
