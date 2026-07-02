import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { MdCheckCircle } from 'react-icons/md'
import { MdMoreVert } from 'react-icons/md'
import './CandidatePanel.css'

function CandidatePanel({ resumeFiles }) {
    const [shortlistSize, setShortlistSize] = useState('50')
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)

    const hasContent = resumeFiles.length > 0

    return (
        <div className="candidate-panel">
            <div className="candidate-panel-header">
                <div className="candidate-header-left">
                    <div className="shortlist-dropdown">
                        <label>Shortlist size</label>
                        <motion.button
                            className="dropdown-button"
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                            whileHover={{ backgroundColor: '#222222' }}
                        >
                            <span>Top {shortlistSize}</span>
                            <span className="dropdown-arrow">▼</span>
                        </motion.button>

                        {isDropdownOpen && (
                            <motion.div
                                className="dropdown-menu"
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.15 }}
                            >
                                {['10', '25', '50', '100'].map((size) => (
                                    <button
                                        key={size}
                                        className={`dropdown-item ${shortlistSize === size ? 'active' : ''}`}
                                        onClick={() => {
                                            setShortlistSize(size)
                                            setIsDropdownOpen(false)
                                        }}
                                    >
                                        Top {size}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </div>
                </div>

                <motion.button
                    className="candidate-menu-btn"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <MdMoreVert />
                </motion.button>
            </div>

            <div className="candidate-panel-content">
                {!hasContent ? (
                    <div className="candidate-empty-state">
                        <MdCheckCircle className="candidate-empty-icon" />
                        <h2 className="candidate-empty-title">Ranked shortlist will appear here</h2>
                        <p className="candidate-empty-subtitle">
                            Add a job description and upload resumes, then verify to start processing.
                        </p>
                    </div>
                ) : (
                    <div className="candidate-list">
                        <p className="candidate-loading">Processing resumes...</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default CandidatePanel