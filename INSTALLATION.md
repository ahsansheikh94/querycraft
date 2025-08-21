# QueryCraft Installation Guide

## Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
./start-app.sh
```

### Option 2: Manual Setup

## Prerequisites

- **Python 3.8+** (Python 3.11 or 3.12 recommended for best compatibility)
- **Node.js 18+**
- **MongoDB** (local or cloud)
- **OpenAI API Key**

## Backend Installation

### 1. Create Virtual Environment

```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. If Installation Fails

#### Option A: Use Compatible Versions

```bash
pip install -r requirements-compatible.txt
```

#### Option B: Install Dependencies Manually

```bash
pip install Flask==2.3.3
pip install pymongo==4.5.0
pip install Flask-JWT-Extended==4.5.3
pip install Flask-CORS==4.0.0
pip install bcrypt==4.0.1
pip install openai==1.3.0
pip install python-dotenv==1.0.0
pip install marshmallow==3.20.1
pip install marshmallow-mongoengine==0.4.0
pip install python-dateutil==2.8.2
pip install gunicorn==21.2.0
pip install flask-limiter==3.5.0
```

### 4. Configure Environment

```bash
cp env.example .env
# Edit .env with your configuration
```

### 5. Start Backend

```bash
python app.py
```

## Frontend Installation

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Configure Environment

```bash
echo "VITE_API_URL=http://localhost:5000/api" > .env
```

### 3. Start Frontend

```bash
npm run dev
```

## Troubleshooting

### Python Version Issues

If you're using Python 3.13 and encountering compatibility issues:

1. **Use Python 3.11 or 3.12** (recommended)
2. **Or use the compatible requirements file**:
   ```bash
   pip install -r requirements-compatible.txt
   ```

### Pydantic Installation Issues

The `pydantic` package was removed from requirements as it's not used in the codebase. If you see pydantic-related errors:

1. **Skip pydantic installation** - it's not required
2. **Use the compatible requirements file** which excludes pydantic

### MongoDB Connection Issues

1. **Ensure MongoDB is running**:

   ```bash
   mongod
   ```

2. **Check connection string** in `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017/sql_query_generator
   ```

### Port Already in Use

If ports 5000 or 3000 are already in use:

1. **Find and kill the process**:

   ```bash
   lsof -ti:5000 | xargs kill -9  # Backend
   lsof -ti:3000 | xargs kill -9  # Frontend
   ```

2. **Or change ports** in the respective configuration files

### Permission Issues

If you encounter permission issues:

1. **Use sudo** (not recommended for development):

   ```bash
   sudo ./start-app.sh
   ```

2. **Fix file permissions**:
   ```bash
   chmod +x start-app.sh
   ```

## Environment Variables

### Backend (.env)

```env
MONGODB_URI=mongodb://localhost:27017/sql_query_generator
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
OPENAI_API_KEY=your-openai-api-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

## Verification

After installation, verify everything is working:

1. **Backend**: http://localhost:5000
2. **Frontend**: http://localhost:3000
3. **API Health**: http://localhost:5000/api/health

## Common Issues

### "Module not found" errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### "Port already in use" errors

- Kill existing processes or change ports
- Check if other applications are using the ports

### "MongoDB connection failed" errors

- Ensure MongoDB is running
- Check connection string in .env file
- Verify MongoDB is accessible

### "OpenAI API key invalid" errors

- Ensure you have a valid OpenAI API key
- Check the key in your .env file
- Verify you have sufficient credits

## Support

If you continue to have issues:

1. Check the console output for specific error messages
2. Ensure all prerequisites are installed
3. Try the manual installation steps
4. Check the troubleshooting section above
5. Create an issue in the repository with your error details
