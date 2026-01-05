from flask import Flask, render_template, request, jsonify
import uuid
import threading
import requests
import time

from config import API_KEY, SD_API_URL
from models import Job
from queue_manager import job_queue, job_store

SD_URL = SD_API_URL

app = Flask(__name__)
app.template_folder = "static"
# ---------------- WORKER (SAFE BACKGROUND THREAD) ---------------- #

_worker_started = False
def worker_loop():
    while True:
        job = job_queue.get()
        try:
            job.status = "running"
            job.progress = 0

            payload = {
                "prompt": job.prompt,
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

            # 🔥 ONE call only
            r = requests.post(
                f"{SD_URL}/sdapi/v1/txt2img",
                json=payload,
                timeout=300
            ).json()

            # SD is DONE here
            image_base64 = r["images"][0]

            job.result = f"data:image/png;base64,{image_base64}"
            job.progress = 100
            job.status = "done"

        except Exception as e:
            job.status = "error"
            job.error = str(e)

        finally:
            job_queue.task_done()

def start_worker():
    global _worker_started
    if _worker_started:
        return
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    _worker_started = True

start_worker()

# ---------------- UI ---------------- #

@app.route("/")
def ui():
    return render_template("index.html", api_key=API_KEY)

@app.route("/ping")
def ping():
    return "OK"

# ---------------- JOB API ---------------- #

@app.route("/api/generate", methods=["POST"])
def generate():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

    prompt = request.json.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    job_id = str(uuid.uuid4())
    job = Job(job_id, prompt)

    job_store[job_id] = job
    job_queue.put(job)

    return jsonify({"job_id": job_id})

@app.route("/api/status/<job_id>")
def status(job_id):
    job = job_store.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "status": job.status,
        "progress": job.progress,
        "result": job.result,
        "error": job.error
    })

@app.route("/api/queue")
def queue_status():
    return jsonify([
        {
            "id": j.id,
            "status": j.status,
            "progress": j.progress
        }
        for j in job_store.values()
    ])

# ---------------- SD PROXY APIs ---------------- #

@app.route("/api/sd/progress")
def sd_progress():
    p = requests.get(f"{SD_URL}/sdapi/v1/progress").json()

    preview = None
    if p.get("current_image"):
        preview = f"data:image/png;base64,{p['current_image']}"

    return jsonify({
        "progress": int(p["progress"] * 100),
        "step": p["state"]["sampling_step"],
        "steps": p["state"]["sampling_steps"],
        "eta": round(p["eta_relative"], 1),
        "preview": preview
    })


@app.route("/api/sd/gpu")
def sd_gpu():
    m = requests.get(f"{SD_URL}/sdapi/v1/memory").json()
    cuda = m.get("ram", {})
    return jsonify({
        "used": round(cuda.get("used", 0) / 1024, 1),
        "total": round(cuda.get("total", 0) / 1024, 1)
    })

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
