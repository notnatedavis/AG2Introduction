//   web/frontend/src/components/SessionItem.js

// ----- Imports -----
import React from 'react';
import './SessionItem.css';

// ----- Main -----
function SessionItem({ session, isActive, onSelect, onStop }) {
  const statusColor = {
    starting: '#fbbf24',
    running: '#34d399',
    stopping: '#f87171',
    finished: '#9ca3af'
  }[session.status] || '#9ca3af';

  return (
    <div className={`session-item ${isActive ? 'active' : ''}`} onClick={onSelect}>
      <div className="session-info">
        <span className="session-id">{session.id}</span>
        <span className="session-workflow">{session.workflow}</span>
        <span className="session-status" style={{ backgroundColor: statusColor }}></span>
      </div>
      <div className="session-task">{session.task}</div>
      <div className="session-meta">
        <span>{session.message_count} messages</span>
        <button
          className="btn-stop"
          onClick={(e) => { e.stopPropagation(); onStop(); }}
          title="Stop session"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

export default SessionItem;