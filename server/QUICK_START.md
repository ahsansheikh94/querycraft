# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key

### 2. Quick Setup

**On macOS/Linux:**

```bash
cd server
./start.sh
```

**On Windows:**

```cmd
cd server
start.bat
```

### 3. Configure Environment

Edit the `.env` file that was created:

```env
MONGODB_URI=mongodb://localhost:27017/sql_query_generator
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Start MongoDB

```bash
mongod
```

### 5. Run the Application

The startup script will automatically:

- Create virtual environment
- Install dependencies
- Start the Flask server

Server will be available at: `http://localhost:5000`

### 6. Test the API

```bash
python test_api.py
```

### 7. Create Sample Data

```bash
python seed_data.py
```

## 📋 API Quick Test

### Register User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Create Project

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "My Database",
    "description": "Test database"
  }'
```

### Add Schema

```bash
curl -X POST http://localhost:5000/api/projects/PROJECT_ID/schema \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "schemas": [
      {
        "table_name": "users",
        "table_schema": {
          "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": true},
            {"name": "username", "type": "VARCHAR(50)", "unique": true},
            {"name": "email", "type": "VARCHAR(100)", "unique": true}
          ]
        }
      }
    ]
  }'
```

### Generate SQL Query

```bash
curl -X POST http://localhost:5000/api/projects/PROJECT_ID/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_input": "Show me all users"
  }'
```

## 🔧 Troubleshooting

### MongoDB Connection Issues

- Make sure MongoDB is running: `mongod`
- Check connection string in `.env`
- For cloud MongoDB, use connection string with authentication

### OpenAI API Issues

- Verify your API key is correct
- Check API key has sufficient credits
- Ensure API key has access to GPT-3.5-turbo

### Port Already in Use

- Change port in `.env`: `FLASK_PORT=5001`
- Or kill existing process: `lsof -ti:5000 | xargs kill -9`

### Permission Issues

- Make startup script executable: `chmod +x start.sh`
- Run with sudo if needed (not recommended)

## 📚 Next Steps

1. **Read the full documentation**: `README.md`
2. **Explore the API**: Use Postman or curl
3. **Build a frontend**: Connect to the API endpoints
4. **Deploy to production**: Follow production deployment guide

## 🆘 Need Help?

- Check the logs in the terminal
- Review error messages in API responses
- Ensure all environment variables are set
- Verify MongoDB and OpenAI connections
