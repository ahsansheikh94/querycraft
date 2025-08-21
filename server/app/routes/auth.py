from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import ValidationError
import logging

from ..models.user import User
from ..utils.validators import UserRegistrationSchema, UserLoginSchema

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Rate limiting for auth endpoints
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint"""
    try:
        # Validate input
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        # Save user to database
        user.save()
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.get_public_data(),
                'access_token': access_token
            },
            'message': 'User registered successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': list(e.messages.values())
        }), 400
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'errors': [str(e)]
        }), 400
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred during registration']
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """User login endpoint"""
    try:
        # Validate input
        schema = UserLoginSchema()
        data = schema.load(request.get_json())
        
        # Authenticate user
        user = User.authenticate(data['email'], data['password'])
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials',
                'errors': ['Email or password is incorrect']
            }), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.get_public_data(),
                'access_token': access_token
            },
            'message': 'Login successful'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': list(e.messages.values())
        }), 400
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred during login']
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find user
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['User account not found']
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.get_public_data()
            },
            'message': 'User information retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred']
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh JWT token"""
    try:
        # Get user ID from current token
        user_id = get_jwt_identity()
        
        # Find user
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['User account not found']
            }), 404
        
        # Generate new token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            },
            'message': 'Token refreshed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred during token refresh']
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find user
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['User account not found']
            }), 404
        
        # Get update data
        data = request.get_json()
        
        # Validate and update fields
        update_fields = {}
        
        if 'username' in data:
            if len(data['username']) < 3 or len(data['username']) > 50:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username',
                    'errors': ['Username must be between 3 and 50 characters']
                }), 400
            update_fields['username'] = data['username']
        
        if 'email' in data:
            # Validate email format
            from ..utils.validators import validate_email_format
            try:
                validate_email_format(data['email'])
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': 'Invalid email',
                    'errors': [str(e)]
                }), 400
            update_fields['email'] = data['email']
        
        # Update user
        if update_fields:
            user.update(**update_fields)
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.get_public_data()
            },
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred during profile update']
        }), 500
