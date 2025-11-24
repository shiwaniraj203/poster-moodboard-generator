import React, { useState } from 'react';
import './App.css';
import QuotePoster from './components/QuotePoster';
import Moodboard from './components/Moodboard';

function App() {
  const [activeTab, setActiveTab] = useState('quote');

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎨 Poster & Moodboard Generator</h1>
        <p>Create beautiful quote posters and vision boards</p>
      </header>

      <div className="tab-navigation">
        <button
          className={activeTab === 'quote' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('quote')}
        >
          📝 Quote Poster
        </button>
        <button
          className={activeTab === 'moodboard' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('moodboard')}
        >
          🖼️ Moodboard
        </button>
      </div>

      <div className="content">
        {activeTab === 'quote' ? <QuotePoster /> : <Moodboard />}
      </div>

      <footer className="app-footer">
        <p>Built with FastAPI + React | Internship Assignment</p>
      </footer>
    </div>
  );
}

export default App;