//   web/frontend/src/components/Message.js
//   Updated with fallback handling for missing or non‑string content

// ----- Imports -----
import React from 'react';
import './Message.css';

// ----- Main -----
function Message({ message }) {
  // Determine sender class
  const senderClass = `message-${message.sender.toLowerCase()}`;
  
  // Handle content that might be an object (e.g., from LLM)
  let content = message.content;
  if (typeof content === 'object' && content !== null) {
    content = content.content || JSON.stringify(content);
  }
  if (content === undefined || content === null) {
    content = '[Empty message]';
  }

  return (
    <div className={`message ${senderClass}`}>
      <div className="message-header">
        <span className="message-sender">{message.sender}</span>
        <span className="message-time">
          {new Date(message.timestamp * 1000).toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">{content}</div>
    </div>
  );
}

export default Message;