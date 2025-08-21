import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://ahsansheikh:SJRFpH4wd5Nh7BOC@ac-cez5jqk-shard-00-00.sgydplo.mongodb.net:27017,ac-cez5jqk-shard-00-01.sgydplo.mongodb.net:27017,ac-cez5jqk-shard-00-02.sgydplo.mongodb.net:27017/querycraft?replicaSet=atlas-wac6w7-shard-0&ssl=true&authSource=admin'
    MONGODB_DB = 'sql_query_generator'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '100/hour')
    RATE_LIMIT_AUTH = os.environ.get('RATE_LIMIT_AUTH', '10/minute')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_DEBUG = False
    
    # Override with production settings
    MONGODB_URI = os.environ.get('MONGODB_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/sql_query_generator_test'
    MONGODB_DB = 'sql_query_generator_test'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
