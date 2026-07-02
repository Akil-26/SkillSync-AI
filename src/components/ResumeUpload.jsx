import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { MdUploadFile } from 'react-icons/md'
import './ResumeUpload.css'

function ResumeUpload({ resumeFiles, setResumeFiles }) {
    const [isDragging, setIsDragging] = useState(false)

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)

        const files = Array.from(e.dataTransfer.files)
        if (files.length > 0) {
            setResumeFiles([...resumeFiles, ...files])
        }
    }

    const handleFileInput = (e) => {
        const files = Array.from(e.target.files)
        if (files.length > 0) {
            setResumeFiles([...resumeFiles, ...files])
        }
    }

    const handleClear = () => {
        setResumeFiles([])
    }

    return (
        <div className="resume-upload-section">
            <h3 className="resume-upload-title">Resumes</h3>

            <motion.div
                className={`resume-upload-box ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                whileHover={{ borderColor: '#4a9eff' }}
                transition={{ duration: 0.2 }}
            >
                <input
                    type="file"
                    id="resume-file-input"
                    multiple
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                    accept=".pdf,.doc,.docx"
                />
                <label htmlFor="resume-file-input" className="resume-upload-label">
                    <MdUploadFile className="resume-upload-icon" />
                    <p className="resume-upload-text">Drop PDFs or a folder, any format</p>
                </label>
            </motion.div>

            <div className="resume-stats">
                <span className="resume-count">{resumeFiles.length.toLocaleString()} files added</span>
                {resumeFiles.length > 0 && (
                    <button className="resume-clear" onClick={handleClear}>
                        Clear
                    </button>
                )}
            </div>

            <motion.button
                className="resume-verify-btn"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                disabled={resumeFiles.length === 0}
            >
                Verify details
            </motion.button>
        </div>
    )
}

export default ResumeUpload