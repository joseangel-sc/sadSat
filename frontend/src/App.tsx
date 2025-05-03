import './App.css'
import HelloWorld from './components/HelloWorld'

function App() {
  return (
    <div className="app">
      <h1>FastAPI + React Integration Demo</h1>
      <div className="card">
        <HelloWorld />
      </div>
      <p className="info">
        This application demonstrates integration between a FastAPI backend and React frontend
      </p>
    </div>
  )
}

export default App
