from datetime import datetime
from bson import ObjectId
from ..utils.database import get_collection, serialize_document, serialize_documents

class Project:
    """Project model for MongoDB"""
    
    def __init__(self, name, user_id, description=None, _id=None, created_at=None, updated_at=None):
        self.name = name
        self.user_id = user_id
        self.description = description
        self._id = _id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'name': self.name,
            'user_id': self.user_id,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create project from dictionary"""
        return cls(
            name=data.get('name'),
            user_id=data.get('user_id'),
            description=data.get('description'),
            _id=data.get('_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def save(self):
        """Save project to database"""
        collection = get_collection('projects')
        
        # Check if project with same name exists for this user
        existing_project = collection.find_one({
            'user_id': self.user_id,
            'name': self.name
        })
        
        if existing_project and existing_project['_id'] != self._id:
            raise ValueError("Project with this name already exists for this user")
        
        if self._id:
            # Update existing project
            self.updated_at = datetime.utcnow()
            collection.update_one(
                {'_id': self._id},
                {'$set': self.to_dict()}
            )
        else:
            # Insert new project
            project_data = self.to_dict()
            result = collection.insert_one(project_data)
            self._id = result.inserted_id
        
        return self
    
    @classmethod
    def find_by_id(cls, project_id, user_id=None):
        """Find project by ID, optionally filtered by user"""
        collection = get_collection('projects')
        query = {'_id': ObjectId(project_id)}
        if user_id:
            query['user_id'] = user_id
        
        project_data = collection.find_one(query)
        return cls.from_dict(project_data) if project_data else None
    
    @classmethod
    def find_by_user(cls, user_id, page=1, per_page=10):
        """Find all projects for a user with pagination"""
        collection = get_collection('projects')
        
        # Calculate skip value for pagination
        skip = (page - 1) * per_page
        
        # Get total count
        total = collection.count_documents({'user_id': user_id})
        
        # Get projects with pagination
        projects_data = collection.find(
            {'user_id': user_id}
        ).sort('updated_at', -1).skip(skip).limit(per_page)
        
        projects = [cls.from_dict(data) for data in projects_data]
        
        return {
            'projects': projects,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }

    @classmethod
    def find_by_user_offset(cls, user_id, skip, limit):
        """Paginate user projects by skip/limit (sorted by updated_at desc)."""
        collection = get_collection('projects')
        total = collection.count_documents({'user_id': user_id})
        if limit <= 0:
            return {'projects': [], 'total': total}
        projects_data = (
            collection.find({'user_id': user_id})
            .sort('updated_at', -1)
            .skip(skip)
            .limit(limit)
        )
        projects = [cls.from_dict(data) for data in projects_data]
        return {'projects': projects, 'total': total}

    def update(self, **kwargs):
        """Update project fields"""
        collection = get_collection('projects')
        
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            self.updated_at = datetime.utcnow()
            update_data['updated_at'] = self.updated_at
            
            collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        
        return self
    
    def delete(self):
        """Delete project and all associated data"""
        collection = get_collection('projects')
        
        # Delete project
        collection.delete_one({'_id': self._id})
        
        # Delete associated schemas
        schemas_collection = get_collection('schemas')
        schemas_collection.delete_many({'project_id': str(self._id)})
        
        # Delete associated queries
        queries_collection = get_collection('queries')
        queries_collection.delete_many({'project_id': str(self._id)})
    
    def get_public_data(self):
        """Get public project data"""
        return {
            'id': str(self._id),
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_project_stats(cls, project_id):
        """Get project statistics"""
        schemas_collection = get_collection('schemas')
        queries_collection = get_collection('queries')
        
        schema_count = schemas_collection.count_documents({'project_id': str(project_id)})
        query_count = queries_collection.count_documents({'project_id': str(project_id)})
        
        return {
            'schema_count': schema_count,
            'query_count': query_count
        }
