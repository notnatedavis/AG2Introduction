#   web/routes.py
#   API endpoints and view routes for the web interface

# ----- Imports -----
from flask import render_template, request, jsonify, Response
import json
import time
from .agent_manager import agent_manager

# ----- Helper Functions -----
def register_routes(app) :
    
    @app.route('/')
    def index() :
        # serve the main dashboard
        return render_template('index.html')
    
    @app.route('/api/sessions', methods=['GET'])
    def list_sessions() :
        # return list of active session IDs and their status
        sessions = agent_manager.list_sessions()
        return jsonify(sessions)
    
    @app.route('/api/sessions', methods=['POST'])
    def create_session() :
        # create a new agent session
        data = request.get_json()
        workflow = data.get('workflow', 'webpage')
        task = data.get('task', '')
        session_id = agent_manager.create_session(workflow, task)
        return jsonify({'session_id': session_id})
    
    @app.route('/api/sessions/<session_id>', methods=['DELETE'])
    def stop_session(session_id) :
        # stop and remove a session
        success = agent_manager.stop_session(session_id)
        return jsonify({'success': success})
    
    @app.route('/api/sessions/<session_id>/messages')
    def stream_messages(session_id) :
        # server-sent events stream for real-time conversation
        def generate() :
            # get the message queue for this session
            queue = agent_manager.get_message_queue(session_id)
            if not queue :
                yield f"event: error\ndata: Session not found\n\n"
                return
            
            # send past messages first
            session = agent_manager.get_session(session_id)
            if session and session.get('messages'):
                for msg in session['messages']:
                    yield f"data: {json.dumps(msg)}\n\n"
            # then stream new messages as they arrive
            while True :
                try :
                    msg = queue.get(timeout=30)  # wait up to 30 seconds
                    yield f"data: {json.dumps(msg)}\n\n"
                except :
                    # no message in 30 seconds, send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"
                    continue
        return Response(generate(), mimetype="text/event-stream")
    
    @app.route('/api/sessions/<session_id>/control', methods=['POST'])
    def send_control(session_id) :
        # send control signals to a session (e.g., pause, resume, terminate)
        data = request.get_json()
        action = data.get('action')
        if action == 'terminate':
            success = agent_manager.terminate_session(session_id)
            return jsonify({'success': success})
        # add other actions as needed
        return jsonify({'success': False, 'error': 'Unknown action'})