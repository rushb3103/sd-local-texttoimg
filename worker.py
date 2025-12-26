import threading
import time
from queue_manager import job_queue, job_store
from sd_client import generate

def worker_loop():
    while True:
        job = job_queue.get()
        job.status = "running"

        try:
            result = generate(job.prompt)
            job.result = result
            job.status = "done"
        except Exception as e:
            job.error = str(e)
            job.status = "error"

        job_queue.task_done()

def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
