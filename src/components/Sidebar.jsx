import React, { useEffect, useState } from 'react'
import './Sidebar.css'
import { rankCandidates, listRuns, getRun } from '../api'

function Sidebar({
  jobDescription, setJobDescription,
  topK, setTopK,
  results, setResults,
  runId, setRunId,
  loading, setLoading,
  error, setError,
}) {
  const [history, setHistory] = useState([])

  const loadHistory = async () => {
    try {
      setHistory(await listRuns())
    } catch {
      // history is best-effort
    }
  }

  useEffect(() => { loadHistory() }, [])

  const handleRank = async () => {
    setError(null)
    setLoading(true)
    try {
      const data = await rankCandidates(jobDescription, Number(topK))
      setResults(data.results)
      setRunId(data.run_id)
      loadHistory()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLoadRun = async (id) => {
    setError(null)
    setLoading(true)
    try {
      const run = await getRun(id)
      setJobDescription(run.job_description)
      setTopK(run.top_k)
      setResults(run.results)
      setRunId(run.id)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">SkillSync AI</h1>
        <p className="sidebar-subtitle">Candidate ranking</p>
      </div>

      <div className="job-description-section">
        <h3 className="job-description-title">Job description</h3>
        <textarea
          className="job-description-textarea"
          placeholder="Paste the JD text"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={10}
        />
      </div>

      <div className="shortlist-size-section">
        <label>Shortlist size</label>
        <select value={topK} onChange={(e) => setTopK(e.target.value)}>
          {[10, 25, 50, 100].map((n) => <option key={n} value={n}>Top {n}</option>)}
        </select>
      </div>

      <button className="rank-btn" onClick={handleRank} disabled={loading || !jobDescription.trim()}>
        {loading ? 'Ranking…' : 'Rank candidates'}
      </button>

      {error && <p className="error-text">{error}</p>}

      <div className="history-section">
        <h3 className="history-title">Past searches</h3>
        {history.length === 0 && <p className="history-empty">No searches yet</p>}
        <ul className="history-list">
          {history.map((h) => (
            <li key={h.id}>
              <button
                className={`history-item ${runId === h.id ? 'active' : ''}`}
                onClick={() => handleLoadRun(h.id)}
              >
                <span className="history-date">{h.created_at}</span>
                <span className="history-snippet">{h.job_description_snippet}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default Sidebar
