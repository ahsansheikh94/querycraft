@echo off

REM SQL Query Generator - Startup Script for Windows

echo 🚀 Starting SQL Query Generator Flask Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy env.example .env
    echo ⚠️ Please edit .env file with your configuration before running the application.
    echo    Required: MONGODB_URI, SECRET_KEY, JWT_SECRET_KEY, OPENAI_API_KEY
    pause
    exit /b 1
)

REM Check if MongoDB is running (optional)
echo 🔍 Checking MongoDB connection...
python -c "import pymongo; client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000); client.admin.command('ping'); print('✅ MongoDB is running')" 2>nul
if errorlevel 1 (
    echo ⚠️ MongoDB connection failed. Make sure MongoDB is running.
    echo    You can start MongoDB with: mongod
)

REM Start the application
echo 🌟 Starting Flask application...
echo    Server will be available at: http://localhost:5000
echo    API endpoints: http://localhost:5000/api
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
