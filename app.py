from flask import Flask, render_template, request, jsonify
import uuid

from config import API_KEY
from models import Job
from queue_manager import job_queue, job_store
from worker import start_worker

app = Flask(__name__)
start_worker()

@app.route("/")
def ui():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "OK"

@app.route("/api/generate", methods=["POST"])
def generate():
    if request.headers.get("X-API-KEY") != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    job_id = str(uuid.uuid4())
    job = Job(id=job_id, prompt=prompt)

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
        "result": job.result,
        "error": job.error
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
