from datetime import datetime
from bson import ObjectId
import bcrypt
from ..utils.database import get_collection
from ..utils.validators import validate_email_format, validate_password_strength

class User:
    """User model for MongoDB"""
    
    def __init__(self, username, email, password=None, password_hash=None, _id=None, created_at=None):
        self.username = username
        self.email = email
        self.password = password
        self.password_hash = password_hash
        self._id = _id
        self.created_at = created_at or datetime.utcnow()
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        return cls(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            _id=data.get('_id'),
            created_at=data.get('created_at')
        )
    
    def save(self):
        """Save user to database"""
        collection = get_collection('users')
        
        # Validate input
        validate_email_format(self.email)
        if self.password:
            validate_password_strength(self.password)
            self.password_hash = self.hash_password(self.password)
        
        # Check if user already exists
        existing_user = collection.find_one({
            '$or': [
                {'email': self.email},
                {'username': self.username}
            ]
        })
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        # Insert user
        user_data = self.to_dict()
        result = collection.insert_one(user_data)
        self._id = result.inserted_id
        return self
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        collection = get_collection('users')
        user_data = collection.find_one({'email': email})
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        collection = get_collection('users')
        user_data = collection.find_one({'_id': ObjectId(user_id)})
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        collection = get_collection('users')
        user_data = collection.find_one({'username': username})
        return cls.from_dict(user_data) if user_data else None
    
    def update(self, **kwargs):
        """Update user fields"""
        collection = get_collection('users')
        
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            collection.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        
        return self
    
    def delete(self):
        """Delete user from database"""
        collection = get_collection('users')
        collection.delete_one({'_id': self._id})
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user with email and password"""
        user = cls.find_by_email(email)
        if user and user.verify_password(password, user.password_hash):
            return user
        return None
    
    def get_public_data(self):
        """Get public user data (without sensitive information)"""
        return {
            'id': str(self._id),
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
