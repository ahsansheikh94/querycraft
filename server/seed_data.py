#!/usr/bin/env python3
"""
Seed data script for SQL Query Generator
This script creates sample data for testing the application
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models.user import User
from app.models.project import Project
from app.models.schema import Schema
from app.models.query import Query
from app.utils.database import get_db

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    
    # Create sample user
    try:
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        user.save()
        print(f"Created user: {user.username}")
    except ValueError as e:
        print(f"User already exists or error: {e}")
        # Try to find existing user
        user = User.find_by_email("test@example.com")
        if not user:
            print("Could not create or find user")
            return
    
    # Create sample project
    try:
        project = Project(
            name="E-commerce Database",
            user_id=str(user._id),
            description="Sample e-commerce database with users, products, and orders"
        )
        project.save()
        print(f"Created project: {project.name}")
    except ValueError as e:
        print(f"Project already exists or error: {e}")
        # Try to find existing project
        projects = Project.find_by_user(str(user._id))
        if projects['projects']:
            project = projects['projects'][0]
        else:
            print("Could not create or find project")
            return
    
    # Create sample schemas
    sample_schemas = [
        {
            "table_name": "users",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "username", "type": "VARCHAR(50)", "unique": True, "not_null": True},
                    {"name": "email", "type": "VARCHAR(100)", "unique": True, "not_null": True},
                    {"name": "password_hash", "type": "VARCHAR(255)", "not_null": True},
                    {"name": "created_at", "type": "TIMESTAMP", "not_null": True},
                    {"name": "updated_at", "type": "TIMESTAMP"}
                ]
            }
        },
        {
            "table_name": "products",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR(100)", "not_null": True},
                    {"name": "description", "type": "TEXT"},
                    {"name": "price", "type": "DECIMAL(10,2)", "not_null": True},
                    {"name": "category_id", "type": "INTEGER"},
                    {"name": "stock_quantity", "type": "INTEGER", "not_null": True},
                    {"name": "created_at", "type": "TIMESTAMP", "not_null": True}
                ]
            }
        },
        {
            "table_name": "categories",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR(50)", "not_null": True},
                    {"name": "description", "type": "TEXT"},
                    {"name": "parent_id", "type": "INTEGER"}
                ]
            }
        },
        {
            "table_name": "orders",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "user_id", "type": "INTEGER", "not_null": True},
                    {"name": "order_date", "type": "TIMESTAMP", "not_null": True},
                    {"name": "total_amount", "type": "DECIMAL(10,2)", "not_null": True},
                    {"name": "status", "type": "VARCHAR(20)", "not_null": True},
                    {"name": "shipping_address", "type": "TEXT"}
                ]
            }
        },
        {
            "table_name": "order_items",
            "table_schema": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "order_id", "type": "INTEGER", "not_null": True},
                    {"name": "product_id", "type": "INTEGER", "not_null": True},
                    {"name": "quantity", "type": "INTEGER", "not_null": True},
                    {"name": "unit_price", "type": "DECIMAL(10,2)", "not_null": True},
                    {"name": "total_price", "type": "DECIMAL(10,2)", "not_null": True}
                ]
            }
        }
    ]
    
    try:
        Schema.bulk_save_schemas(str(project._id), sample_schemas)
        print(f"Created {len(sample_schemas)} schemas")
    except Exception as e:
        print(f"Error creating schemas: {e}")
    
    # Create sample queries
    sample_queries = [
        {
            "user_input": "Show me all users who registered in the last 30 days",
            "generated_sql": "SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) ORDER BY created_at DESC;",
            "explanation": "This query retrieves all users who registered within the last 30 days, ordered by registration date in descending order."
        },
        {
            "user_input": "Find products with low stock (less than 10 items)",
            "generated_sql": "SELECT id, name, stock_quantity FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity ASC;",
            "explanation": "This query finds products with stock quantity less than 10, ordered by stock quantity in ascending order."
        },
        {
            "user_input": "Get total sales by category",
            "generated_sql": "SELECT c.name as category_name, SUM(oi.total_price) as total_sales FROM categories c JOIN products p ON c.id = p.category_id JOIN order_items oi ON p.id = oi.product_id GROUP BY c.id, c.name ORDER BY total_sales DESC;",
            "explanation": "This query calculates total sales for each category by joining categories, products, and order_items tables."
        }
    ]
    
    for query_data in sample_queries:
        try:
            query = Query(
                project_id=str(project._id),
                user_input=query_data["user_input"],
                generated_sql=query_data["generated_sql"],
                explanation=query_data["explanation"]
            )
            query.save()
            print(f"Created sample query: {query_data['user_input'][:50]}...")
        except Exception as e:
            print(f"Error creating sample query: {e}")
    
    print("Sample data creation completed!")

def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        create_sample_data()

if __name__ == "__main__":
    main()
