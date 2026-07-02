import React, { useState } from 'react'
import './App.css'
import Layout from './components/Layout'

function App() {
    const [jobDescription, setJobDescription] = useState('')
    const [preferences, setPreferences] = useState(['Senior', 'Remote ok'])
    const [jdFiles, setJdFiles] = useState([])
    const [resumeFiles, setResumeFiles] = useState([])

    return (
        <Layout
            jobDescription={jobDescription}
            setJobDescription={setJobDescription}
            preferences={preferences}
            setPreferences={setPreferences}
            jdFiles={jdFiles}
            setJdFiles={setJdFiles}
            resumeFiles={resumeFiles}
            setResumeFiles={setResumeFiles}
        />
    )
}

export default App