//   web/frontend/src/components/Message.js

// ----- Imports -----
import React from 'react';
import './Message.css';

// ----- Main -----
function Message({ message }) {
  const senderClass = `message-${message.sender.toLowerCase()}`;

  return (
    <div className={`message ${senderClass}`}>
      <div className="message-header">
        <span className="message-sender">{message.sender}</span>
        <span className="message-time">
          {new Date(message.timestamp * 1000).toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">{message.content}</div>
    </div>
  );
}

export default Message;