import React from 'react'
import { BrowserRouter as Router } from 'react-router-dom'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-50 text-white">
        {/* App content will be added here */}
        <h1 className="text-2xl font-bold text-primary-500">ZenMedia Player</h1>
      </div>
    </Router>
  )
}

export default App