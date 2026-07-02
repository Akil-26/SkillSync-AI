import React from 'react'
import './Sidebar.css'
import JobDescription from './JobDescription'
import PreferenceTags from './PreferenceTags'
import ResumeUpload from './ResumeUpload'

function Sidebar({
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
        <div className="sidebar">
            <div className="sidebar-header">
                <h1 className="sidebar-title">Senior ML Engineer — screening room</h1>
                <p className="sidebar-subtitle">Room created just now</p>
            </div>

            <JobDescription
                jobDescription={jobDescription}
                setJobDescription={setJobDescription}
                jdFiles={jdFiles}
                setJdFiles={setJdFiles}
            />

            <PreferenceTags
                preferences={preferences}
                setPreferences={setPreferences}
            />

            <ResumeUpload
                resumeFiles={resumeFiles}
                setResumeFiles={setResumeFiles}
            />
        </div>
    )
}

export default Sidebar