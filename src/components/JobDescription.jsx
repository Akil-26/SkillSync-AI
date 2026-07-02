import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { MdUploadFile } from 'react-icons/md'
import './JobDescription.css'

function JobDescription({
    jobDescription,
    setJobDescription,
    jdFiles,
    setJdFiles
}) {
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
            setJdFiles([...jdFiles, ...files])
        }
    }

    const handleFileInput = (e) => {
        const files = Array.from(e.target.files)
        if (files.length > 0) {
            setJdFiles([...jdFiles, ...files])
        }
    }

    const removeFile = (index) => {
        setJdFiles(jdFiles.filter((_, i) => i !== index))
    }

    return (
        <div className="job-description-section">
            <h3 className="job-description-title">Job description</h3>

            <motion.div
                className={`job-description-upload ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                whileHover={{ borderColor: '#4a9eff' }}
                transition={{ duration: 0.2 }}
            >
                <input
                    type="file"
                    id="jd-file-input"
                    multiple
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                    accept=".pdf,.doc,.docx,.txt"
                />
                <label htmlFor="jd-file-input" className="job-description-label">
                    <MdUploadFile className="job-description-icon" />
                    <p className="job-description-text">Drop a JD file, any format</p>
                </label>
            </motion.div>

            {jdFiles.length > 0 && (
                <div className="job-description-files">
                    {jdFiles.map((file, index) => (
                        <div key={index} className="file-item">
                            <span className="file-name">{file.name}</span>
                            <button
                                className="file-remove"
                                onClick={() => removeFile(index)}
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="job-description-divider">
                <span>or</span>
            </div>

            <textarea
                className="job-description-textarea"
                placeholder="Paste the JD text instead"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
            />
        </div>
    )
}

export default JobDescription