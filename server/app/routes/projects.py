from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from ..models.project import Project
from ..utils.validators import ProjectSchema, PaginationSchema
from ..data.builtin_catalog import (
    builtin_project_count,
    list_builtin_projects_with_stats,
    try_get_builtin_project_public,
    attach_stats,
    get_builtin_project_stats,
    is_builtin_project_id,
    READONLY_MESSAGE,
)

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
        
        page = pagination_data['page']
        per_page = pagination_data['per_page']
        B = builtin_project_count()
        builtins_full = list_builtin_projects_with_stats()

        start_global = (page - 1) * per_page
        end_global = start_global + per_page

        builtin_part = [
            builtins_full[i]
            for i in range(start_global, min(end_global, B))
        ]

        ua = max(0, start_global - B)
        ub_exclusive = max(0, end_global - B)
        user_limit = max(0, ub_exclusive - ua)

        user_window = Project.find_by_user_offset(user_id, ua, user_limit)

        combined = []
        for item in builtin_part:
            combined.append(item)
        for project in user_window['projects']:
            project_data = project.get_public_data()
            stats = Project.get_project_stats(project_data['id'])
            project_data['stats'] = stats
            combined.append(project_data)

        total_display = B + user_window['total']
        pages = (total_display + per_page - 1) // per_page if per_page else 0

        return jsonify({
            'success': True,
            'data': {
                'projects': combined,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_display,
                    'pages': pages
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
        
        builtin = try_get_builtin_project_public(project_id)
        if builtin:
            project_data = attach_stats(builtin)
            return jsonify({
                'success': True,
                'data': {
                    'project': project_data
                },
                'message': 'Project retrieved successfully'
            }), 200

        project = Project.find_by_id(project_id, user_id)

        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

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
        
        if is_builtin_project_id(project_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

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
        
        if is_builtin_project_id(project_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

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
        
        if is_builtin_project_id(project_id):
            stats = get_builtin_project_stats(project_id)
            return jsonify({
                'success': True,
                'data': {
                    'project_id': project_id,
                    'stats': stats
                },
                'message': 'Project statistics retrieved successfully'
            }), 200

        project = Project.find_by_id(project_id, user_id)

        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

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
