import React, { useState } from 'react'
import './App.css'
import Layout from './components/Layout'

function App() {
  const [jobDescription, setJobDescription] = useState('')
  const [topK, setTopK] = useState(50)
  const [results, setResults] = useState(null)
  const [runId, setRunId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const state = {
    jobDescription, setJobDescription,
    topK, setTopK,
    results, setResults,
    runId, setRunId,
    loading, setLoading,
    error, setError,
  }

  return <Layout {...state} />
}

export default App
