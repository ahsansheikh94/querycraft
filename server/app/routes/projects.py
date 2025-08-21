from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from ..models.user import User
from ..models.project import Project
from ..utils.validators import ProjectSchema, PaginationSchema

logger = logging.getLogger(__name__)

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Validate input
        schema = ProjectSchema()
        data = schema.load(request.get_json())
        
        # Create project
        project = Project(
            name=data['name'],
            user_id=user_id,
            description=data.get('description')
        )
        
        # Save project
        project.save()
        
        return jsonify({
            'success': True,
            'data': {
                'project': project.get_public_data()
            },
            'message': 'Project created successfully'
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
        logger.error(f"Create project error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while creating project']
        }), 500

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects for the current user"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get pagination parameters
        schema = PaginationSchema()
        pagination_data = schema.load(request.args)
        
        # Get projects with pagination
        result = Project.find_by_user(
            user_id=user_id,
            page=pagination_data['page'],
            per_page=pagination_data['per_page']
        )
        
        # Get project statistics
        projects_with_stats = []
        for project in result['projects']:
            project_data = project.get_public_data()
            stats = Project.get_project_stats(project_data['id'])
            project_data['stats'] = stats
            projects_with_stats.append(project_data)
        
        return jsonify({
            'success': True,
            'data': {
                'projects': projects_with_stats,
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages']
                }
            },
            'message': 'Projects retrieved successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': list(e.messages.values())
        }), 400
        
    except Exception as e:
        logger.error(f"Get projects error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving projects']
        }), 500

@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get a specific project by ID"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find project
        project = Project.find_by_id(project_id, user_id)
        
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Get project statistics
        project_data = project.get_public_data()
        stats = Project.get_project_stats(project_id)
        project_data['stats'] = stats
        
        return jsonify({
            'success': True,
            'data': {
                'project': project_data
            },
            'message': 'Project retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get project error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving project']
        }), 500

@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find project
        project = Project.find_by_id(project_id, user_id)
        
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Validate input
        schema = ProjectSchema()
        data = schema.load(request.get_json())
        
        # Update project
        project.update(
            name=data['name'],
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'project': project.get_public_data()
            },
            'message': 'Project updated successfully'
        }), 200
        
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
        logger.error(f"Update project error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while updating project']
        }), 500

@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find project
        project = Project.find_by_id(project_id, user_id)
        
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Delete project (this will also delete associated schemas and queries)
        project.delete()
        
        return jsonify({
            'success': True,
            'data': {},
            'message': 'Project deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete project error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while deleting project']
        }), 500

@projects_bp.route('/<project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """Get detailed statistics for a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Find project
        project = Project.find_by_id(project_id, user_id)
        
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Get project statistics
        stats = Project.get_project_stats(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'stats': stats
            },
            'message': 'Project statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get project stats error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving project statistics']
        }), 500
