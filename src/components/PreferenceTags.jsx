import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { MdAdd } from 'react-icons/md'
import './PreferenceTags.css'

function PreferenceTags({ preferences, setPreferences }) {
    const [isAddingNew, setIsAddingNew] = useState(false)
    const [newTag, setNewTag] = useState('')

    const handleAddTag = () => {
        if (newTag.trim() && !preferences.includes(newTag.trim())) {
            setPreferences([...preferences, newTag.trim()])
            setNewTag('')
            setIsAddingNew(false)
        }
    }

    const handleRemoveTag = (tag) => {
        setPreferences(preferences.filter(pref => pref !== tag))
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleAddTag()
        }
        if (e.key === 'Escape') {
            setIsAddingNew(false)
            setNewTag('')
        }
    }

    return (
        <div className="preference-tags-section">
            <h3 className="preference-tags-title">Preferences</h3>

            <div className="preference-tags-container">
                {preferences.map((pref, index) => (
                    <motion.div
                        key={index}
                        className="preference-tag active"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <span>{pref}</span>
                        <button
                            className="tag-remove"
                            onClick={() => handleRemoveTag(pref)}
                        >
                            ✕
                        </button>
                    </motion.div>
                ))}

                {isAddingNew ? (
                    <input
                        type="text"
                        className="preference-tag-input"
                        placeholder="Add preference"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={handleKeyPress}
                        onBlur={() => {
                            if (!newTag.trim()) {
                                setIsAddingNew(false)
                            }
                        }}
                        autoFocus
                    />
                ) : (
                    <motion.button
                        className="preference-tag-add"
                        onClick={() => setIsAddingNew(true)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <MdAdd className="tag-add-icon" />
                        <span>Add</span>
                    </motion.button>
                )}
            </div>
        </div>
    )
}

export default PreferenceTags