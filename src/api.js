const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function rankCandidates(jobDescription, topK) {
  const res = await fetch(`${API_BASE}/api/rank`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_description: jobDescription, top_k: topK }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Ranking failed')
  return res.json()
}

export async function listRuns() {
  const res = await fetch(`${API_BASE}/api/runs`)
  return res.json()
}

export async function getRun(runId) {
  const res = await fetch(`${API_BASE}/api/runs/${runId}`)
  return res.json()
}
