//   web/frontend/src/components/Conversation.js

// ----- Imports -----
import React, { useState, useEffect, useRef } from 'react';
import Message from './Message';
import { sendMessage } from '../services/api'; // add this
import './Conversation.css';

// ----- Main -----
function Conversation({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
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
      return;
    }

    setMessages([]); // clear previous messages
    const es = new EventSource(`/api/sessions/${sessionId}/messages`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setMessages(prev => [...prev, msg]);
    };

    es.onerror = () => {
      console.log('SSE error or closed');
      es.close();
      eventSourceRef.current = null;
    };

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, [sessionId]); // dependency array now contains only sessionId

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
      </div>
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
          />
          <button type="submit">Send</button>
        </form>
      )}
    </div>
  );
}


export default Conversation;