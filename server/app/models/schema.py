from datetime import datetime
from bson import ObjectId
import json
from ..utils.database import get_collection, serialize_document, serialize_documents
from ..utils.validators import validate_schema_json

class Schema:
    """Schema model for MongoDB"""
    
    def __init__(self, project_id, table_name, table_schema, _id=None, created_at=None):
        self.project_id = project_id
        self.table_name = table_name
        self.table_schema = table_schema
        self._id = _id
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert schema to dictionary"""
        return {
            'project_id': self.project_id,
            'table_name': self.table_name,
            'table_schema': self.table_schema,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create schema from dictionary"""
        return cls(
            project_id=data.get('project_id'),
            table_name=data.get('table_name'),
            table_schema=data.get('table_schema'),
            _id=data.get('_id'),
            created_at=data.get('created_at')
        )
    
    def save(self):
        """Save schema to database"""
        collection = get_collection('schemas')
        
        # Validate schema format
        validate_schema_json(self.table_schema)
        
        # Check if schema with same table name exists for this project
        existing_schema = collection.find_one({
            'project_id': self.project_id,
            'table_name': self.table_name
        })
        
        if existing_schema and existing_schema['_id'] != self._id:
            raise ValueError(f"Schema for table '{self.table_name}' already exists in this project")
        
        if self._id:
            # Update existing schema
            collection.update_one(
                {'_id': self._id},
                {'$set': self.to_dict()}
            )
        else:
            # Insert new schema
            schema_data = self.to_dict()
            result = collection.insert_one(schema_data)
            self._id = result.inserted_id
        
        return self
    
    @classmethod
    def find_by_project(cls, project_id):
        """Find all schemas for a project"""
        collection = get_collection('schemas')
        schemas_data = collection.find({'project_id': project_id}).sort('table_name', 1)
        return [cls.from_dict(data) for data in schemas_data]
    
    @classmethod
    def find_by_id(cls, schema_id, project_id=None):
        """Find schema by ID, optionally filtered by project"""
        collection = get_collection('schemas')
        query = {'_id': ObjectId(schema_id)}
        if project_id:
            query['project_id'] = project_id
        
        schema_data = collection.find_one(query)
        return cls.from_dict(schema_data) if schema_data else None
    
    @classmethod
    def find_by_table_name(cls, project_id, table_name):
        """Find schema by table name within a project"""
        collection = get_collection('schemas')
        schema_data = collection.find_one({
            'project_id': project_id,
            'table_name': table_name
        })
        return cls.from_dict(schema_data) if schema_data else None
    
    def update(self, **kwargs):
        """Update schema fields"""
        collection = get_collection('schemas')
        
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            # Validate schema if table_schema is being updated
            if 'table_schema' in update_data:
                validate_schema_json(update_data['table_schema'])
            
            collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        
        return self
    
    def delete(self):
        """Delete schema from database"""
        collection = get_collection('schemas')
        collection.delete_one({'_id': self._id})
    
    def get_public_data(self):
        """Get public schema data"""
        return {
            'id': str(self._id),
            'project_id': self.project_id,
            'table_name': self.table_name,
            'table_schema': self.table_schema,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def bulk_save_schemas(cls, project_id, schemas_data):
        """Bulk save multiple schemas for a project"""
        collection = get_collection('schemas')
        
        # Validate all schemas first
        for schema_data in schemas_data:
            validate_schema_json(schema_data['table_schema'])
        
        # Delete existing schemas for this project
        collection.delete_many({'project_id': project_id})
        
        # Insert new schemas
        schemas_to_insert = []
        for schema_data in schemas_data:
            schema = cls(
                project_id=project_id,
                table_name=schema_data['table_name'],
                table_schema=schema_data['table_schema']
            )
            schemas_to_insert.append(schema.to_dict())
        
        if schemas_to_insert:
            result = collection.insert_many(schemas_to_insert)
            return [str(id) for id in result.inserted_ids]
        
        return []
    
    @classmethod
    def get_schema_summary(cls, project_id):
        """Get summary of all schemas for a project"""
        schemas = cls.find_by_project(project_id)
        
        summary = {
            'total_tables': len(schemas),
            'tables': []
        }
        
        for schema in schemas:
            table_info = {
                'table_name': schema.table_name,
                'column_count': len(schema.table_schema.get('columns', [])),
                'columns': [col['name'] for col in schema.table_schema.get('columns', [])]
            }
            summary['tables'].append(table_info)
        
        return summary
    
    def get_formatted_schema_for_ai(self):
        """Get schema formatted for AI processing"""
        columns = self.table_schema.get('columns', [])
        
        formatted_columns = []
        for col in columns:
            col_info = f"{col['name']} ({col['type']})"
            
            # Add constraints
            constraints = []
            if col.get('primary_key'):
                constraints.append('PRIMARY KEY')
            if col.get('unique'):
                constraints.append('UNIQUE')
            if col.get('not_null'):
                constraints.append('NOT NULL')
            
            if constraints:
                col_info += f" - {', '.join(constraints)}"
            
            formatted_columns.append(col_info)
        
        return f"Table: {self.table_name}\nColumns: {', '.join(formatted_columns)}"
