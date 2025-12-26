let jobId = null;

async function submitJob() {
  const prompt = document.getElementById("prompt").value;
  document.getElementById("status").innerText = "Queued...";

  const res = await fetch("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": "sd-portfolio-key"
    },
    body: JSON.stringify({ prompt })
  });

  const data = await res.json();
  jobId = data.job_id;

  pollStatus();
}

async function pollStatus() {
  const res = await fetch(`/api/status/${jobId}`);
  const data = await res.json();

  document.getElementById("status").innerText = data.status;

  if (data.status === "done") {
    document.getElementById("result").src =
      "data:image/png;base64," + data.result.images[0];
    return;
  }

  if (data.status === "error") {
    document.getElementById("status").innerText = data.error;
    return;
  }

  setTimeout(pollStatus, 3000);
}
