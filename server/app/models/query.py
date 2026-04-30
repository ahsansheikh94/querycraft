from datetime import datetime, timedelta
from bson import ObjectId
from ..utils.database import get_collection, serialize_document, serialize_documents
from ..utils.validators import validate_sql_query

class Query:
    """Query model for MongoDB"""
    
    def __init__(self, project_id, user_input, generated_sql, explanation=None, _id=None, created_at=None, user_id=None):
        self.project_id = project_id
        self.user_id = user_id
        self.user_input = user_input
        self.generated_sql = generated_sql
        self.explanation = explanation
        self._id = _id
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert query to dictionary"""
        return {
            'project_id': self.project_id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'generated_sql': self.generated_sql,
            'explanation': self.explanation,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create query from dictionary"""
        return cls(
            project_id=data.get('project_id'),
            user_id=data.get('user_id'),
            user_input=data.get('user_input'),
            generated_sql=data.get('generated_sql'),
            explanation=data.get('explanation'),
            _id=data.get('_id'),
            created_at=data.get('created_at')
        )
    
    def save(self):
        """Save query to database"""
        collection = get_collection('queries')
        
        # Validate SQL query for security
        if self.generated_sql:
            validate_sql_query(self.generated_sql)
        
        query_data = self.to_dict()
        result = collection.insert_one(query_data)
        self._id = result.inserted_id
        return self
    
    @classmethod
    def find_by_id(cls, query_id, project_id=None):
        """Find query by ID, optionally filtered by project"""
        collection = get_collection('queries')
        query = {'_id': ObjectId(query_id)}
        if project_id:
            query['project_id'] = project_id
        
        query_data = collection.find_one(query)
        return cls.from_dict(query_data) if query_data else None
    
    @classmethod
    def find_by_project(cls, project_id, page=1, per_page=10, user_id=None):
        """Find all queries for a project with pagination"""
        collection = get_collection('queries')

        # Calculate skip value for pagination
        skip = (page - 1) * per_page

        mongo_query = {'project_id': project_id}
        if user_id is not None:
            mongo_query['user_id'] = user_id

        # Get total count
        total = collection.count_documents(mongo_query)

        # Get queries with pagination
        queries_data = collection.find(mongo_query).sort('created_at', -1).skip(skip).limit(per_page)
        
        queries = [cls.from_dict(data) for data in queries_data]
        
        return {
            'queries': queries,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @classmethod
    def search_queries(cls, project_id, search_term, page=1, per_page=10, user_id=None):
        """Search queries by user input or generated SQL"""
        collection = get_collection('queries')

        # Calculate skip value for pagination
        skip = (page - 1) * per_page

        # Create search query
        search_query = {
            'project_id': project_id,
            '$or': [
                {'user_input': {'$regex': search_term, '$options': 'i'}},
                {'generated_sql': {'$regex': search_term, '$options': 'i'}},
                {'explanation': {'$regex': search_term, '$options': 'i'}}
            ]
        }
        if user_id is not None:
            search_query['user_id'] = user_id
        
        # Get total count
        total = collection.count_documents(search_query)
        
        # Get queries with pagination
        queries_data = collection.find(search_query).sort('created_at', -1).skip(skip).limit(per_page)
        
        queries = [cls.from_dict(data) for data in queries_data]
        
        return {
            'queries': queries,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'search_term': search_term
        }
    
    def update(self, **kwargs):
        """Update query fields"""
        collection = get_collection('queries')
        
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            # Validate SQL query if being updated
            if 'generated_sql' in update_data:
                validate_sql_query(update_data['generated_sql'])
            
            collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        
        return self
    
    def delete(self):
        """Delete query from database"""
        collection = get_collection('queries')
        collection.delete_one({'_id': self._id})
    
    def get_public_data(self):
        """Get public query data"""
        return {
            'id': str(self._id),
            'project_id': self.project_id,
            'user_input': self.user_input,
            'generated_sql': self.generated_sql,
            'explanation': self.explanation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_query_stats(cls, project_id):
        """Get query statistics for a project"""
        collection = get_collection('queries')
        
        # Total queries
        total_queries = collection.count_documents({'project_id': project_id})
        
        # Queries by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_queries = collection.count_documents({
            'project_id': project_id,
            'created_at': {'$gte': thirty_days_ago}
        })
        
        # Most common query patterns (simplified analysis)
        pipeline = [
            {'$match': {'project_id': project_id}},
            {'$group': {
                '_id': '$user_input',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        
        common_patterns = list(collection.aggregate(pipeline))
        
        return {
            'total_queries': total_queries,
            'recent_queries': recent_queries,
            'common_patterns': common_patterns
        }
    
    @classmethod
    def get_recent_queries(cls, project_id, limit=5):
        """Get recent queries for a project"""
        collection = get_collection('queries')
        queries_data = collection.find(
            {'project_id': project_id}
        ).sort('created_at', -1).limit(limit)
        
        return [cls.from_dict(data) for data in queries_data]
