//   web/static/js/main.js

let currentSessionId = null;
let eventSource = null;

document.addEventListener('DOMContentLoaded', () => {
    loadSessions();

    document.getElementById('start-session').addEventListener('click', startSession);
    document.getElementById('stop-session').addEventListener('click', stopCurrentSession);
});

function loadSessions() {
    fetch('/api/sessions')
        .then(res => res.json())
        .then(sessions => {
            const list = document.getElementById('session-list');
            list.innerHTML = '';
            sessions.forEach(s => {
                const div = document.createElement('div');
                div.className = 'session-item';
                div.innerHTML = `
                    <span>${s.id} (${s.workflow}) - ${s.status} - ${s.message_count} msgs</span>
                    <button onclick="selectSession('${s.id}')">View</button>
                `;
                list.appendChild(div);
            });
        });
}

function startSession() {
    const workflow = document.getElementById('workflow-select').value;
    const task = document.getElementById('task-input').value;
    if (!task) {
        alert('Please enter a task');
        return;
    }

    fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow, task })
    })
    .then(res => res.json())
    .then(data => {
        selectSession(data.session_id);
        loadSessions();
    });
}

function selectSession(sessionId) {
    // Close previous stream
    if (eventSource) {
        eventSource.close();
    }

    currentSessionId = sessionId;
    document.getElementById('current-session').innerText = `Session: ${sessionId}`;

    // Clear conversation box
    document.getElementById('conversation-box').innerHTML = '';

    // Start SSE stream for this session
    eventSource = new EventSource(`/api/sessions/${sessionId}/messages`);
    eventSource.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        addMessageToConversation(msg);
    };
    eventSource.onerror = () => {
        console.log('SSE connection closed or error');
        eventSource.close();
    };
}

function stopCurrentSession() {
    if (!currentSessionId) return;
    fetch(`/api/sessions/${currentSessionId}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (eventSource) {
                    eventSource.close();
                }
                currentSessionId = null;
                document.getElementById('current-session').innerText = 'No session selected';
                document.getElementById('conversation-box').innerHTML = '';
                loadSessions();
            }
        });
}

function addMessageToConversation(msg) {
    const box = document.getElementById('conversation-box');
    const div = document.createElement('div');
    div.className = `message sender-${msg.sender.toLowerCase()}`;
    div.innerHTML = `<strong>${msg.sender}:</strong> ${escapeHtml(msg.content)}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

// Simple escape to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}