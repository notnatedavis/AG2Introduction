//   web/frontend/src/components/NewSessionForm.js

// ----- Imports -----
import React, { useState } from 'react';
import { createSession } from '../services/api';
import './NewSessionForm.css';

// ----- Main -----
function NewSessionForm({ onSessionCreated }) {
  const [workflow, setWorkflow] = useState('webpage');
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!task.trim()) return;
    setLoading(true);
    try {
      const { session_id } = await createSession(workflow, task);
      onSessionCreated(session_id);
      setTask('');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-session-form card">
      <h2>Start New Session</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="workflow">Workflow</label>
          <select
            id="workflow"
            value={workflow}
            onChange={(e) => setWorkflow(e.target.value)}
            disabled={loading}
          >
            <option value="webpage">Webpage Designer</option>
            <option value="coding">Coding Assistant</option>
            <option value="team">Team Orchestration</option>

          </select>
        </div>
        <div className="form-group">
          <label htmlFor="task">Task</label>
          <textarea
            id="task"
            rows="3"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe what you want the agent to do..."
            disabled={loading}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Starting...' : 'Launch Session'}
        </button>
      </form>
    </div>
  );
}

export default NewSessionForm;