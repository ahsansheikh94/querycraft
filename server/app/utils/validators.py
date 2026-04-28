from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import re

class UserRegistrationSchema(Schema):
    """Schema for user registration validation"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class UserLoginSchema(Schema):
    """Schema for user login validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class ProjectSchema(Schema):
    """Schema for project creation/update validation"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))

class TableSchemaSchema(Schema):
    """Schema for table schema validation"""
    table_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    table_schema = fields.Dict(required=True)

class SchemaInputSchema(Schema):
    """Schema for schema input validation"""
    schemas = fields.List(fields.Nested(TableSchemaSchema), required=True, validate=validate.Length(min=1))

class QueryInputSchema(Schema):
    """Schema for query input validation"""
    user_input = fields.Str(required=True, validate=validate.Length(min=1, max=1000))

class PaginationSchema(Schema):
    """Schema for pagination parameters"""
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=10, validate=validate.Range(min=1, max=100))

def validate_schema_json(schema_data):
    """Validate that schema data contains valid JSON structure"""
    try:
        if not isinstance(schema_data, dict):
            raise ValidationError("Schema must be a JSON object")
        
        if 'columns' not in schema_data:
            raise ValidationError("Schema must contain 'columns' field")
        
        if not isinstance(schema_data['columns'], list):
            raise ValidationError("Columns must be an array")
        
        for column in schema_data['columns']:
            if not isinstance(column, dict):
                raise ValidationError("Each column must be an object")
            
            if 'name' not in column or 'type' not in column:
                raise ValidationError("Each column must have 'name' and 'type' fields")
            
            if not isinstance(column['name'], str) or not isinstance(column['type'], str):
                raise ValidationError("Column name and type must be strings")
        
        return True
        
    except Exception as e:
        raise ValidationError(f"Invalid schema format: {str(e)}")

def validate_sql_query(query):
    """Basic SQL injection prevention validation.

    Uses whole-word / phrase regex matching so identifiers like CREATED_AT do not
    falsely match dangerous substrings such as CREATE or UPDATE.
    """
    if not isinstance(query, str):
        raise ValidationError("Invalid SQL query")

    # Longer phrases first so e.g. UNION ALL is classified before UNION.
    dangerous_patterns = [
        (r'\bEXECUTE\s+IMMEDIATE\b', 'EXECUTE IMMEDIATE'),
        (r'\bUNION\s+ALL\b', 'UNION ALL'),
        (r'\bINFORMATION_SCHEMA\b', 'INFORMATION_SCHEMA'),
        (r'\bDROP\b', 'DROP'),
        (r'\bDELETE\b', 'DELETE'),
        (r'\bTRUNCATE\b', 'TRUNCATE'),
        (r'\bALTER\b', 'ALTER'),
        (r'\bCREATE\b', 'CREATE'),
        (r'\bINSERT\b', 'INSERT'),
        (r'\bUPDATE\b', 'UPDATE'),
        (r'\bEXEC\b', 'EXEC'),
        (r'\bEXECUTE\b', 'EXECUTE'),
        (r'\bUNION\b', 'UNION'),
        (r'\bSYSTEM\b', 'SYSTEM'),
        (r'\bSYS\b', 'SYS'),
        (r'\bDUAL\b', 'DUAL'),
    ]

    for pattern, label in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValidationError(f"Query contains potentially dangerous keyword: {label}")

    return True

def validate_email_format(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email format")
    return True

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long")
    
    # Check for at least one letter and one number
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError("Password must contain at least one letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one number")
    
    return True

class ErrorResponseSchema(Schema):
    """Schema for error responses"""
    success = fields.Bool()
    message = fields.Str()
    errors = fields.List(fields.Str())

class SuccessResponseSchema(Schema):
    """Schema for success responses"""
    success = fields.Bool()
    data = fields.Dict()
    message = fields.Str()
