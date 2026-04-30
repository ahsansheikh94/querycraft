from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import logging

from ..models.schema import Schema
from ..utils.validators import SchemaInputSchema
from ..data.builtin_catalog import (
    user_has_project_access,
    is_builtin_project_id,
    is_builtin_schema_id,
    merged_schema_public_dicts,
    merged_schema_summary,
    find_schema_merged,
    READONLY_MESSAGE,
)

logger = logging.getLogger(__name__)

schema_bp = Blueprint('schema', __name__)

@schema_bp.route('/<project_id>/schema', methods=['POST'])
@jwt_required()
def create_schema(project_id):
    """Create or merge schemas for a project (add/update tables without removing others)"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if is_builtin_project_id(project_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        # Validate input
        schema = SchemaInputSchema()
        data = schema.load(request.get_json())

        # Bulk save: merge into existing project schemas (does not remove other tables)
        Schema.bulk_save_schemas(project_id, data['schemas'])

        schemas_data = merged_schema_public_dicts(project_id)

        return jsonify({
            'success': True,
            'data': {
                'schemas': schemas_data,
                'schema_count': len(schemas_data)
            },
            'message': f'Schemas created successfully for {len(data["schemas"])} table(s)'
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
        logger.error(f"Create schema error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while creating schemas']
        }), 500

@schema_bp.route('/<project_id>/schema', methods=['GET'])
@jwt_required()
def get_schemas(project_id):
    """Get all schemas for a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        schemas_data = merged_schema_public_dicts(project_id)
        summary = merged_schema_summary(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'schemas': schemas_data,
                'summary': summary
            },
            'message': 'Schemas retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get schemas error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving schemas']
        }), 500

@schema_bp.route('/<project_id>/schema', methods=['PUT'])
@jwt_required()
def update_schemas(project_id):
    """Update schemas for a project (merges by table name; other tables unchanged)"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if is_builtin_project_id(project_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        # Validate input
        schema = SchemaInputSchema()
        data = schema.load(request.get_json())

        Schema.bulk_save_schemas(project_id, data['schemas'])

        schemas_data = merged_schema_public_dicts(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'schemas': schemas_data,
                'schema_count': len(schemas_data)
            },
            'message': f'Schemas updated successfully for {len(schemas_data)} tables'
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
        logger.error(f"Update schemas error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while updating schemas']
        }), 500

@schema_bp.route('/<project_id>/schema/<schema_id>', methods=['GET'])
@jwt_required()
def get_schema(project_id, schema_id):
    """Get a specific schema by ID"""
    try:
        user_id = get_jwt_identity()

        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        schema = find_schema_merged(schema_id, project_id)
        if not schema:
            return jsonify({
                'success': False,
                'message': 'Schema not found',
                'errors': ['Schema not found']
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'schema': schema.get_public_data()
            },
            'message': 'Schema retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get schema error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving schema']
        }), 500

@schema_bp.route('/<project_id>/schema/<schema_id>', methods=['PUT'])
@jwt_required()
def update_schema(project_id, schema_id):
    """Update a specific schema"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        schema = find_schema_merged(schema_id, project_id)
        if not schema:
            return jsonify({
                'success': False,
                'message': 'Schema not found',
                'errors': ['Schema not found']
            }), 404

        if is_builtin_schema_id(schema_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

        # Get update data
        data = request.get_json()
        
        # Update schema
        update_fields = {}
        if 'table_name' in data:
            update_fields['table_name'] = data['table_name']
        if 'table_schema' in data:
            update_fields['table_schema'] = data['table_schema']
        
        if update_fields:
            schema.update(**update_fields)
        
        return jsonify({
            'success': True,
            'data': {
                'schema': schema.get_public_data()
            },
            'message': 'Schema updated successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'errors': [str(e)]
        }), 400
        
    except Exception as e:
        logger.error(f"Update schema error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while updating schema']
        }), 500

@schema_bp.route('/<project_id>/schema/<schema_id>', methods=['DELETE'])
@jwt_required()
def delete_schema(project_id, schema_id):
    """Delete a specific schema"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        schema = find_schema_merged(schema_id, project_id)
        if not schema:
            return jsonify({
                'success': False,
                'message': 'Schema not found',
                'errors': ['Schema not found']
            }), 404

        if is_builtin_schema_id(schema_id):
            return jsonify({
                'success': False,
                'message': READONLY_MESSAGE,
                'errors': [READONLY_MESSAGE],
            }), 403

        schema.delete()
        
        return jsonify({
            'success': True,
            'data': {},
            'message': 'Schema deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete schema error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while deleting schema']
        }), 500

@schema_bp.route('/<project_id>/schema/summary', methods=['GET'])
@jwt_required()
def get_schema_summary(project_id):
    """Get schema summary for a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        if not user_has_project_access(project_id, user_id):
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404

        summary = merged_schema_summary(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'summary': summary
            },
            'message': 'Schema summary retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get schema summary error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving schema summary']
        }), 500
