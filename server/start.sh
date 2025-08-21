#!/bin/bash

# SQL Query Generator - Startup Script

echo "🚀 Starting SQL Query Generator Flask Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the application."
    echo "   Required: MONGODB_URI, SECRET_KEY, JWT_SECRET_KEY, OPENAI_API_KEY"
    exit 1
fi

# Check if MongoDB is running (optional)
echo "🔍 Checking MongoDB connection..."
python3 -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('✅ MongoDB is running')
except Exception as e:
    print('⚠️  MongoDB connection failed. Make sure MongoDB is running.')
    print('   You can start MongoDB with: mongod')
"

# Start the application
echo "🌟 Starting Flask application..."
echo "   Server will be available at: http://localhost:5000"
echo "   API endpoints: http://localhost:5000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
