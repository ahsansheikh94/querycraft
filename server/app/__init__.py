from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

from .config.config import Config
from .utils.database import init_db
from .routes.auth import auth_bp
from .routes.projects import projects_bp
from .routes.schema import schema_bp
from .routes.queries import queries_bp

# Load environment variables
load_dotenv()

def create_app(config_class=Config):
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_db(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS with proper configuration
    CORS(app, 
         resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', ['*'])}},
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization']
    )
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config.get('RATE_LIMIT_DEFAULT', '100/hour')]
    )
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(schema_bp, url_prefix='/api/projects')
    app.register_blueprint(queries_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'message': 'Resource not found',
            'errors': ['The requested resource was not found']
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred']
        }, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'success': False,
            'message': 'Bad request',
            'errors': ['Invalid request data']
        }, 400
    
    return app
