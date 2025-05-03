import './App.css'
import HelloWorld from './components/HelloWorld'
import DataViewer from './components/DataViewer'
import { useState } from 'react'

function App() {
  const [activeTab, setActiveTab] = useState<'hello' | 'data'>('hello')

  return (
    <div className="app">
      <h1>FastAPI + React Integration Demo</h1>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'hello' ? 'active' : ''}`}
          onClick={() => setActiveTab('hello')}
        >
          Hello World
        </button>
        <button 
          className={`tab ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          Catalog Data
        </button>
      </div>
      
      <div className="card">
        {activeTab === 'hello' ? <HelloWorld /> : <DataViewer />}
      </div>
      
      <p className="info">
        This application demonstrates integration between a FastAPI backend and React frontend
      </p>
    </div>
  )
}

export default App
