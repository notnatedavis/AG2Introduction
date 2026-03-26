//   web/frontend/src/components/Conversation.js
//   Enhanced SSE handling with connection status and real‑time message logging

// ----- Imports -----
import React, { useState, useEffect, useRef } from 'react';
import Message from './Message';
import GraphPanel from './GraphPanel';
import { sendMessage } from '../services/api';
import './Conversation.css';

// ----- Main -----
function Conversation({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [connectionError, setConnectionError] = useState(false);
  const eventSourceRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Clean up any existing EventSource when sessionId changes
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (!sessionId) {
      setMessages([]);
      setConnectionError(false);
      return;
    }

    setMessages([]);
    setConnectionError(false);
    const es = new EventSource(`/api/sessions/${sessionId}/messages`);
    eventSourceRef.current = es;

    // Connection opened
    es.onopen = () => {
      console.log(`SSE connection opened for session ${sessionId}`);
      setConnectionError(false);
    };

    // Handle incoming messages
    es.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log('Received message:', msg);
        setMessages(prev => {
          console.log('New messages length:', prev.length + 1);
          return [...prev, msg];
        });
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    // Handle errors (e.g., connection drop)
    es.onerror = (event) => {
      console.error('SSE error:', event);
      setConnectionError(true);
      // The browser will automatically attempt to reconnect.
    };

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, [sessionId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || !sessionId) return;
    try {
      await sendMessage(sessionId, inputText);
      setInputText('');
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  return (
    <div className="conversation-container">
      <div className="conversation-header">
        <h2>Conversation {sessionId ? `- Session ${sessionId}` : ''}</h2>
        {connectionError && (
          <div className="connection-warning">
            ⚠️ Connection lost. Reconnecting...
          </div>
        )}
      </div>
      {/* New expandable graph panel */}
      {sessionId && <GraphPanel />}
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <Message key={idx} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      {sessionId && (
        <form className="message-input-form" onSubmit={handleSend}>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your response..."
            disabled={connectionError}
          />
          <button type="submit" disabled={connectionError}>Send</button>
        </form>
      )}
    </div>
  );
}

export default Conversation;