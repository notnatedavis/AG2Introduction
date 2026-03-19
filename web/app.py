#   web/app.py

# ----- Imports -----
from flask import Flask
from flask_cors import CORS
from .routes import register_routes
import os

# ----- Main -----
def create_app() :
    # Determine static folder – use React build if available, else default
    react_build = os.path.join(os.path.dirname(__file__), 'frontend/build')
    if os.path.exists(react_build) :
        static_folder = react_build
        template_folder = react_build
    else :
        static_folder = 'static'
        template_folder = 'templates'

    app = Flask(__name__, 
                static_folder=static_folder,
                template_folder=template_folder)
    app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    CORS(app)
    
    register_routes(app)
    return app