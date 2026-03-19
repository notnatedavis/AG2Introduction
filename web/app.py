#   web/app.py
#   Flask application factory

# ----- Imports -----
from flask import Flask
from flask_cors import CORS
from .routes import register_routes

# ----- Main -----
def create_app() :
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    CORS(app)  # Enable CORS for API calls
    
    # Register routes
    register_routes(app)
    
    return app