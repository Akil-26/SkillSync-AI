import React from 'react'
import './Layout.css'
import Sidebar from './Sidebar'
import CandidatePanel from './CandidatePanel'

function Layout({
    jobDescription,
    setJobDescription,
    preferences,
    setPreferences,
    jdFiles,
    setJdFiles,
    resumeFiles,
    setResumeFiles
}) {
    return (
        <div className="layout-container">
            <div className="layout-sidebar">
                <Sidebar
                    jobDescription={jobDescription}
                    setJobDescription={setJobDescription}
                    preferences={preferences}
                    setPreferences={setPreferences}
                    jdFiles={jdFiles}
                    setJdFiles={setJdFiles}
                    resumeFiles={resumeFiles}
                    setResumeFiles={setResumeFiles}
                />
            </div>
            <div className="layout-main">
                <CandidatePanel resumeFiles={resumeFiles} />
            </div>
        </div>
    )
}

export default Layout