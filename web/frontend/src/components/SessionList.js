//   web/frontend/src/components/SessionList.js

// ----- Imports -----
import React from 'react';
import SessionItem from './SessionItem';
import './SessionList.css';

// ----- Main -----
function SessionList({ sessions, currentSessionId, onSelectSession, onStopSession, loading }) {
  return (
    <div className="session-list card">
      <h2>Active Sessions</h2>
      {loading && <p className="loading">Loading sessions...</p>}
      {!loading && sessions.length === 0 && (
        <p className="no-sessions">No active sessions. Start a new one!</p>
      )}
      <div className="session-items">
        {sessions.map(session => (
          <SessionItem
            key={session.id}
            session={session}
            isActive={session.id === currentSessionId}
            onSelect={() => onSelectSession(session.id)}
            onStop={() => onStopSession(session.id)}
          />
        ))}
      </div>
    </div>
  );
}

export default SessionList;