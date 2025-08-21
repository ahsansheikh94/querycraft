#!/bin/bash

# QueryCraft - Full Stack Application Startup Script

echo "🚀 Starting QueryCraft Full Stack Application..."
echo "================================================"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check if MongoDB is running
echo "🔍 Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Starting MongoDB..."
    mongod --fork --logpath /tmp/mongod.log
    sleep 2
fi

# Check backend port
echo "🔍 Checking backend port..."
if ! check_port 5000; then
    echo "❌ Backend port 5000 is already in use. Please stop the existing process."
    exit 1
fi

# Check frontend port
echo "🔍 Checking frontend port..."
if ! check_port 3000; then
    echo "❌ Frontend port 3000 is already in use. Please stop the existing process."
    exit 1
fi

# Start backend
echo "🔧 Starting Flask Backend..."
cd server

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Trying with compatible versions..."
    pip install -r requirements-compatible.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your Python version and try manually."
        exit 1
    fi
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Required: MONGODB_URI, SECRET_KEY, JWT_SECRET_KEY, OPENAI_API_KEY"
    read -p "Press Enter to continue after editing .env file..."
fi

# Start backend in background
echo "🌟 Starting Flask backend on http://localhost:5000"
python3 app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🔧 Starting React Frontend..."
cd ../web

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating frontend .env file..."
    echo "VITE_API_URL=http://localhost:5000/api" > .env
fi

# Start frontend in background
echo "🌟 Starting React frontend on http://localhost:3000"
npm run start &
FRONTEND_PID=$!

echo ""
echo "🎉 QueryCraft is starting up!"
echo "=============================="
echo "📊 Backend API: http://localhost:5000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Documentation: http://localhost:5000/api"
echo ""
echo "⏳ Please wait a moment for both services to fully start..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down QueryCraft..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
