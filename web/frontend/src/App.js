//   web/frontend/src/App.js

// ----- Imports -----
import React, { useState, useEffect } from 'react';
import SessionList from './components/SessionList';
import NewSessionForm from './components/NewSessionForm';
import Conversation from './components/Conversation';
import { fetchSessions, deleteSession } from './services/api';
import './App.css';

// ----- Main -----
function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadSessions = async () => {
    setLoading(true);
    const data = await fetchSessions();
    setSessions(data);
    setLoading(false);
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleSessionCreated = (newSessionId) => {
    loadSessions();
    setCurrentSessionId(newSessionId);
  };

  const handleStopSession = async (sessionId) => {
    await deleteSession(sessionId);
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
    }
    loadSessions();
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AG2 Multi‑Agent Control Dashboard</h1>
      </header>
      <main className="app-main">
        <div className="left-panel">
          <NewSessionForm onSessionCreated={handleSessionCreated} />
          <SessionList
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelectSession={setCurrentSessionId}
            onStopSession={handleStopSession}
            loading={loading}
          />
        </div>
        <div className="right-panel">
          <Conversation sessionId={currentSessionId} />
        </div>
      </main>
    </div>
  );
}

export default App;