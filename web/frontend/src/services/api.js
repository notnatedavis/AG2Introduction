//   web/frontend/src/services/api.js

const API_BASE = '/api';

export const fetchSessions = async () => {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return res.json();
};

export const createSession = async (workflow, task) => {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workflow, task })
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
};

export const deleteSession = async (sessionId) => {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete session');
  return res.json();
};

export const sendMessage = async (sessionId, message) => {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error('Failed to send message');
  return res.json();
};