from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from openai import APIError
import logging

from ..models.project import Project
from ..models.query import Query
from ..services.openai_service import OpenAIService
from ..utils.validators import QueryInputSchema, PaginationSchema

logger = logging.getLogger(__name__)

queries_bp = Blueprint('queries', __name__)

@queries_bp.route('/projects/<project_id>/query', methods=['POST'])
@jwt_required()
def generate_query(project_id):
    """Generate SQL query from natural language input"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Verify project ownership
        project = Project.find_by_id(project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Validate input
        schema = QueryInputSchema()
        data = schema.load(request.get_json())

        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning('Generate query called but OPENAI_API_KEY is not set')
            return jsonify({
                'success': False,
                'message': 'OpenAI API key is not configured',
                'errors': ['Set OPENAI_API_KEY in the server environment to enable SQL generation'],
            }), 503

        # Initialize OpenAI service
        openai_service = OpenAIService(api_key)

        # Generate SQL query
        result = openai_service.generate_sql_query(data['user_input'], project_id)
        
        # Save query to database
        query = Query(
            project_id=project_id,
            user_input=data['user_input'],
            generated_sql=result['sql_query'],
            explanation=result['explanation']
        )
        query.save()
        
        return jsonify({
            'success': True,
            'data': {
                'query': query.get_public_data(),
                'generated_sql': result['sql_query'],
                'explanation': result['explanation']
            },
            'message': 'SQL query generated successfully'
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

    except APIError as e:
        logger.error(f'Generate query OpenAI API error: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Language model request failed',
            'errors': [str(e)],
        }), 502

    except Exception as e:
        logger.error(f"Generate query error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while generating query']
        }), 500

@queries_bp.route('/projects/<project_id>/queries', methods=['GET'])
@jwt_required()
def get_queries(project_id):
    """Get all queries for a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Verify project ownership
        project = Project.find_by_id(project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Get pagination parameters
        schema = PaginationSchema()
        pagination_data = schema.load(request.args)
        
        # Get search term if provided
        search_term = request.args.get('search', '')
        
        if search_term:
            # Search queries
            result = Query.search_queries(
                project_id=project_id,
                search_term=search_term,
                page=pagination_data['page'],
                per_page=pagination_data['per_page']
            )
        else:
            # Get all queries
            result = Query.find_by_project(
                project_id=project_id,
                page=pagination_data['page'],
                per_page=pagination_data['per_page']
            )
        
        # Convert queries to public data
        queries_data = [query.get_public_data() for query in result['queries']]
        
        response_data = {
            'queries': queries_data,
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total': result['total'],
                'pages': result['pages']
            }
        }
        
        if search_term:
            response_data['search_term'] = search_term
        
        return jsonify({
            'success': True,
            'data': response_data,
            'message': 'Queries retrieved successfully'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'errors': list(e.messages.values())
        }), 400
        
    except Exception as e:
        logger.error(f"Get queries error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving queries']
        }), 500

@queries_bp.route('/queries/<query_id>', methods=['GET'])
@jwt_required()
def get_query(query_id):
    """Get a specific query by ID"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get query
        query = Query.find_by_id(query_id)
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query not found',
                'errors': ['Query not found']
            }), 404
        
        # Verify project ownership
        project = Project.find_by_id(query.project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Access denied',
                'errors': ['You do not have access to this query']
            }), 403
        
        return jsonify({
            'success': True,
            'data': {
                'query': query.get_public_data()
            },
            'message': 'Query retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get query error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving query']
        }), 500

@queries_bp.route('/queries/<query_id>/explain', methods=['GET'])
@jwt_required()
def explain_query(query_id):
    """Get detailed explanation for a query"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get query
        query = Query.find_by_id(query_id)
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query not found',
                'errors': ['Query not found']
            }), 404
        
        # Verify project ownership
        project = Project.find_by_id(query.project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Access denied',
                'errors': ['You do not have access to this query']
            }), 403
        
        # Initialize OpenAI service
        openai_service = OpenAIService(current_app.config['OPENAI_API_KEY'])
        
        # Generate detailed explanation
        explanation = openai_service.explain_query(query_id, query.project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'query_id': query_id,
                'detailed_explanation': explanation
            },
            'message': 'Query explanation generated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Explain query error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while explaining query']
        }), 500

@queries_bp.route('/queries/<query_id>/improve', methods=['GET'])
@jwt_required()
def suggest_improvements(query_id):
    """Get improvement suggestions for a query"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get query
        query = Query.find_by_id(query_id)
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query not found',
                'errors': ['Query not found']
            }), 404
        
        # Verify project ownership
        project = Project.find_by_id(query.project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Access denied',
                'errors': ['You do not have access to this query']
            }), 403
        
        # Initialize OpenAI service
        openai_service = OpenAIService(current_app.config['OPENAI_API_KEY'])
        
        # Get improvement suggestions
        suggestions = openai_service.suggest_improvements(query.generated_sql, query.project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'query_id': query_id,
                'suggestions': suggestions
            },
            'message': 'Improvement suggestions generated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Suggest improvements error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while generating suggestions']
        }), 500

@queries_bp.route('/queries/<query_id>', methods=['DELETE'])
@jwt_required()
def delete_query(query_id):
    """Delete a query"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get query
        query = Query.find_by_id(query_id)
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query not found',
                'errors': ['Query not found']
            }), 404
        
        # Verify project ownership
        project = Project.find_by_id(query.project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Access denied',
                'errors': ['You do not have access to this query']
            }), 403
        
        # Delete query
        query.delete()
        
        return jsonify({
            'success': True,
            'data': {},
            'message': 'Query deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete query error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while deleting query']
        }), 500

@queries_bp.route('/projects/<project_id>/queries/stats', methods=['GET'])
@jwt_required()
def get_query_stats(project_id):
    """Get query statistics for a project"""
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Verify project ownership
        project = Project.find_by_id(project_id, user_id)
        if not project:
            return jsonify({
                'success': False,
                'message': 'Project not found',
                'errors': ['Project not found or access denied']
            }), 404
        
        # Get query statistics
        stats = Query.get_query_stats(project_id)
        
        # Get recent queries
        recent_queries = Query.get_recent_queries(project_id, limit=5)
        recent_queries_data = [query.get_public_data() for query in recent_queries]
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'stats': stats,
                'recent_queries': recent_queries_data
            },
            'message': 'Query statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Get query stats error: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred while retrieving query statistics']
        }), 500
