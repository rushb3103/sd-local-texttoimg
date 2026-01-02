async function submitJob() {
  const prompt = document.getElementById("prompt").value;
  const status = document.getElementById("status");
  const img = document.getElementById("result");

  status.innerText = "Submitting...";
  img.src = "";

  const res = await fetch("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": "YOUR_API_KEY_HERE"
    },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  if (!res.ok) {
    status.innerText = data.error || "Error";
    return;
  }

  pollStatus(data.job_id);
}

async function pollStatus(jobId) {
  const status = document.getElementById("status");
  const img = document.getElementById("result");

  const interval = setInterval(async () => {
    const res = await fetch(`/api/status/${jobId}`);
    const data = await res.json();

    status.innerText = data.status;

    if (data.status === "done") {
      img.src = data.result;
      clearInterval(interval);
    }

    if (data.status === "error") {
      status.innerText = data.error;
      clearInterval(interval);
    }
  }, 1500);
}
