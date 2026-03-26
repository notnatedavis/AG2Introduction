#   web/routes.py
#   Enhanced SSE streaming with context preservation and detailed logging

# ----- Imports -----
from flask import render_template, request, jsonify, Response, send_from_directory, stream_with_context
import json
import os
import logging
from .agent_manager import agent_manager
from queue import Empty

# Setup logger for this module
logger = logging.getLogger(__name__)

# ----- Main -----
def register_routes(app) :
    
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
            try :
                if session and session.messages :
                    for msg in session.messages :
                        yield f"data: {json.dumps(msg)}\n\n"
            except Exception as e : 
                logger.error(f"Error replaying messages for {session_id}: {e}")
                # Continue anyway – don't kill the generator

            while True :
                try :
                    msg = queue.get(timeout=15)   # shorter timeout for faster heartbeats
                    yield f"data: {json.dumps(msg)}\n\n"
                except Empty:
                    yield f": heartbeat\n\n"
                except Exception as e:
                    logger.error(f"Unexpected error in SSE generator for {session_id}: {e}")
                    # Keep going – don't break the connection
                    continue

        return Response(stream_with_context(generate()), mimetype="text/event-stream")
    
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
        if not message :
            return jsonify({'error': 'Message required'}), 400

        session = agent_manager.get_session(session_id)
        if not session :
            return jsonify({'error': 'Session not found'}), 404

        try :
            session.send_user_input(message)
        except RuntimeError as e :
            return jsonify({'error': str(e)}), 409
        return jsonify({'success': True})