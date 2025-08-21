#!/usr/bin/env python3
"""
Test script for SQL Query Generator API
This script tests the main API endpoints to ensure they're working correctly
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test if the server is running"""
    try:
        response = requests.get("http://localhost:5000/")
        print("✅ Server is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n🔐 Testing User Registration...")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code == 201:
            print("✅ User registration successful")
            return response.json()['data']['access_token']
        elif response.status_code == 400:
            print("⚠️  User might already exist, trying login...")
            return test_user_login()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔐 Testing User Login...")
    
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        if response.status_code == 200:
            print("✅ User login successful")
            return response.json()['data']['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_create_project(token):
    """Test project creation"""
    print("\n📁 Testing Project Creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test E-commerce Database",
        "description": "A test database for e-commerce operations"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects", json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Project creation successful")
            return response.json()['data']['project']['id']
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Project creation error: {e}")
        return None

def test_add_schema(token, project_id):
    """Test schema addition"""
    print("\n🗄️ Testing Schema Addition...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "schemas": [
            {
                "table_name": "users",
                "table_schema": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "username", "type": "VARCHAR(50)", "unique": True, "not_null": True},
                        {"name": "email", "type": "VARCHAR(100)", "unique": True, "not_null": True},
                        {"name": "created_at", "type": "TIMESTAMP", "not_null": True}
                    ]
                }
            },
            {
                "table_name": "products",
                "table_schema": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True},
                        {"name": "name", "type": "VARCHAR(100)", "not_null": True},
                        {"name": "price", "type": "DECIMAL(10,2)", "not_null": True},
                        {"name": "stock_quantity", "type": "INTEGER", "not_null": True}
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects/{project_id}/schema", json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Schema addition successful")
            return True
        else:
            print(f"❌ Schema addition failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Schema addition error: {e}")
        return False

def test_generate_query(token, project_id):
    """Test SQL query generation"""
    print("\n🤖 Testing SQL Query Generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "user_input": "Show me all users who registered in the last 30 days"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/projects/{project_id}/query", json=data, headers=headers)
        if response.status_code == 201:
            print("✅ Query generation successful")
            result = response.json()['data']
            print(f"Generated SQL: {result['generated_sql']}")
            print(f"Explanation: {result['explanation']}")
            return result['query']['id']
        else:
            print(f"❌ Query generation failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Query generation error: {e}")
        return None

def test_get_queries(token, project_id):
    """Test getting project queries"""
    print("\n📊 Testing Query Retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/queries", headers=headers)
        if response.status_code == 200:
            print("✅ Query retrieval successful")
            queries = response.json()['data']['queries']
            print(f"Found {len(queries)} queries")
            return True
        else:
            print(f"❌ Query retrieval failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Query retrieval error: {e}")
        return False

def test_get_projects(token):
    """Test getting user projects"""
    print("\n📁 Testing Project Retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        if response.status_code == 200:
            print("✅ Project retrieval successful")
            projects = response.json()['data']['projects']
            print(f"Found {len(projects)} projects")
            return True
        else:
            print(f"❌ Project retrieval failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Project retrieval error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SQL Query Generator API Test")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        return
    
    # Test authentication
    token = test_user_registration()
    if not token:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test project creation
    project_id = test_create_project(token)
    if not project_id:
        print("❌ Project creation failed. Exiting.")
        return
    
    # Test schema addition
    if not test_add_schema(token, project_id):
        print("❌ Schema addition failed. Exiting.")
        return
    
    # Test query generation (only if OpenAI API key is available)
    if os.getenv('OPENAI_API_KEY'):
        query_id = test_generate_query(token, project_id)
        if query_id:
            print("✅ Query generation test completed")
        else:
            print("⚠️  Query generation test failed (check OpenAI API key)")
    else:
        print("⚠️  Skipping query generation test (no OpenAI API key)")
    
    # Test query retrieval
    test_get_queries(token, project_id)
    
    # Test project retrieval
    test_get_projects(token)
    
    print("\n🎉 API test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
