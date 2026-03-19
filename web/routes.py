#   web/routes.py

# ----- Imports -----
from flask import render_template, request, jsonify, Response, send_from_directory
import json
import os
from .agent_manager import agent_manager

# ----- Main -----
def register_routes(app) :
    
    # API endpoints (unchanged)
    @app.route('/api/sessions', methods=['GET'])
    def list_sessions():
        sessions = agent_manager.list_sessions()
        return jsonify(sessions)

    @app.route('/api/sessions', methods=['POST'])
    def create_session() :
        data = request.get_json()
        workflow = data.get('workflow', 'webpage')
        task = data.get('task', '')
        session_id = agent_manager.create_session(workflow, task)
        return jsonify({'session_id': session_id})

    @app.route('/api/sessions/<session_id>', methods=['DELETE'])
    def stop_session(session_id) :
        success = agent_manager.stop_session(session_id)
        return jsonify({'success': success})

    @app.route('/api/sessions/<session_id>/messages')
    def stream_messages(session_id) :
        def generate() :
            queue = agent_manager.get_message_queue(session_id)
            if not queue :
                yield f"event: error\ndata: Session not found\n\n"
                return
            session = agent_manager.get_session(session_id)
            if session and session.messages :
                for msg in session.messages :
                    yield f"data: {json.dumps(msg)}\n\n"
            while True :
                try :
                    msg = queue.get(timeout=30)
                    yield f"data: {json.dumps(msg)}\n\n"
                except :
                    yield f": heartbeat\n\n"
                    continue
        return Response(generate(), mimetype="text/event-stream")

    @app.route('/api/sessions/<session_id>/control', methods=['POST'])
    def send_control(session_id) :
        data = request.get_json()
        action = data.get('action')
        if action == 'terminate' :
            success = agent_manager.terminate_session(session_id)
            return jsonify({'success': success})
        return jsonify({'success': False, 'error': 'Unknown action'})

    # Serve React static files and catch‑all for client‑side routing
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path) :
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else :
            return send_from_directory(app.static_folder, 'index.html')
        
    @app.route('/api/sessions/<session_id>/message', methods=['POST'])
    def send_message(session_id) :
        data = request.get_json()
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Message required'}), 400

        session = agent_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Feed the message into the session's user input queue
        session.send_user_input(message)
        return jsonify({'success': True})