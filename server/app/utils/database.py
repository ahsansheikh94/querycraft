from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from bson import ObjectId
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MongoDB client
mongo_client = None
db = None

def init_db(app):
    """Initialize MongoDB connection with connection pooling"""
    global mongo_client, db
    
    try:
        # Create MongoDB client with connection pooling
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        
        # Test connection
        mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get database
        db_name = app.config.get('MONGODB_DB', 'sql_query_generator')
        db = mongo_client[db_name]
        
        # Create indexes for better performance
        create_indexes(db)
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise e

def create_indexes(db):
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        db.users.create_index("created_at")
        
        # Projects collection indexes
        db.projects.create_index("user_id")
        db.projects.create_index("created_at")
        db.projects.create_index([("user_id", 1), ("name", 1)])
        
        # Schemas collection indexes
        db.schemas.create_index("project_id")
        db.schemas.create_index([("project_id", 1), ("table_name", 1)], unique=True)
        
        # Queries collection indexes
        db.queries.create_index("project_id")
        db.queries.create_index("created_at")
        db.queries.create_index([("project_id", 1), ("created_at", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise e

def get_db():
    """Get database instance"""
    return db

def get_collection(collection_name):
    """Get MongoDB collection"""
    return db[collection_name]

def close_db():
    """Close MongoDB connection"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId and datetime objects"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_document(doc):
    """Serialize MongoDB document for JSON response"""
    if doc is None:
        return None
    
    # Convert ObjectId to string
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    # Convert datetime objects to ISO format
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            doc[key] = str(value)
    
    return doc

def serialize_documents(docs):
    """Serialize list of MongoDB documents for JSON response"""
    return [serialize_document(doc) for doc in docs]
