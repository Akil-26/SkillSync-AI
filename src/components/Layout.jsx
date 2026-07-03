import React from 'react'
import './Layout.css'
import Sidebar from './Sidebar'
import CandidatePanel from './CandidatePanel'

function Layout(props) {
  return (
    <div className="layout-container">
      <div className="layout-sidebar">
        <Sidebar {...props} />
      </div>
      <div className="layout-main">
        <CandidatePanel {...props} />
      </div>
    </div>
  )
}

export default Layout
