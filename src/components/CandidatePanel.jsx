import React from 'react'
import './CandidatePanel.css'

function CandidatePanel({ results, loading, error }) {
  const hasContent = results && results.length > 0

  return (
    <div className="candidate-panel">
      <div className="candidate-panel-header">
        <h2>Ranked shortlist</h2>
        {hasContent && <span className="candidate-count">{results.length} candidates</span>}
      </div>

      <div className="candidate-panel-content">
        {loading && <p className="candidate-loading">Ranking candidates…</p>}

        {!loading && !hasContent && !error && (
          <div className="candidate-empty-state">
            <h2 className="candidate-empty-title">Ranked shortlist will appear here</h2>
            <p className="candidate-empty-subtitle">
              Paste a job description and click "Rank candidates" to start.
            </p>
          </div>
        )}

        {!loading && hasContent && (
          <table className="candidate-table">
            <thead>
              <tr>
                <th>Rank</th><th>Candidate</th><th>Title</th>
                <th>Experience</th><th>Score</th><th>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr key={r.candidate_id}>
                  <td>{r.rank}</td>
                  <td>{r.candidate_id}</td>
                  <td>{r.current_title || '—'}</td>
                  <td>{r.experience_years != null ? `${r.experience_years} yrs` : '—'}</td>
                  <td>{r.score.toFixed(4)}</td>
                  <td className="candidate-reasoning">{r.justification}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default CandidatePanel
