# QueryCraft - SQL Query Generator

A full-stack application that transforms natural language into SQL queries using AI. Built with Flask backend and React frontend.

## 🚀 Features

### 🤖 AI-Powered SQL Generation

- **Natural Language to SQL**: Convert plain English to SQL queries
- **OpenAI Integration**: Powered by GPT-3.5-turbo for accurate query generation
- **Query Explanation**: AI-generated explanations in plain English
- **Query Improvements**: AI suggestions for query optimization

### 🔐 Authentication & Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password security
- **Protected Routes**: Route guards for authenticated users
- **Rate Limiting**: Protection against API abuse

### 📁 Project Management

- **Multiple Projects**: Create and manage multiple SQL projects
- **Schema Management**: Store and manage database table schemas
- **Query History**: Track and search through generated queries
- **Project Statistics**: Analytics and insights

### 🎨 Modern UI/UX

- **Dark Theme**: Beautiful dark mode with glass morphism
- **Responsive Design**: Mobile-first approach
- **Smooth Animations**: Framer Motion powered transitions
- **Real-time Feedback**: Toast notifications and loading states

## 🏗️ Architecture

### Backend (Flask)

- **Framework**: Flask with Python 3.8+
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT with Flask-JWT-Extended
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Validation**: Marshmallow schemas
- **Security**: bcrypt, rate limiting, CORS

### Frontend (React)

- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with shadcn/ui
- **State Management**: Zustand with persistence
- **API Integration**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Forms**: React Hook Form with Zod validation

## 📦 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB (local or cloud)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd QueryCraft
```

### 2. Start the Full Application

```bash
./start-app.sh
```

This script will:

- Check and start MongoDB
- Set up environment files
- Install dependencies
- Start both backend and frontend

### 3. Manual Setup (Alternative)

#### Backend Setup

```bash
cd server
cp env.example .env
# Edit .env with your configuration
pip install -r requirements.txt
python app.py
```

#### Frontend Setup

```bash
cd web
echo "VITE_API_URL=http://localhost:5000/api" > .env
npm install
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api

## 🔧 Configuration

### Backend Environment Variables

```env
MONGODB_URI=mongodb://localhost:27017/sql_query_generator
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=your-openai-api-key
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:5000/api
```

## 📚 API Endpoints

### Authentication

```
POST /api/auth/register     - User registration
POST /api/auth/login        - User login
GET  /api/auth/me           - Get current user
POST /api/auth/refresh      - Refresh JWT token
```

### Projects

```
POST   /api/projects                    - Create project
GET    /api/projects                    - List user projects
GET    /api/projects/{id}              - Get project details
PUT    /api/projects/{id}              - Update project
DELETE /api/projects/{id}              - Delete project
```

### Schemas

```
POST   /api/projects/{id}/schema       - Create/update schemas
GET    /api/projects/{id}/schema       - Get project schemas
PUT    /api/projects/{id}/schema       - Replace all schemas
```

### Queries

```
POST   /api/projects/{id}/query        - Generate SQL query
GET    /api/projects/{id}/queries      - List project queries
GET    /api/queries/{id}/explain       - Get detailed explanation
GET    /api/queries/{id}/improve       - Get improvement suggestions
```

## 🎯 Usage Examples

### 1. Create a Project

1. Sign up/login to the application
2. Click "New Project" on the dashboard
3. Enter project name and description
4. Save the project

### 2. Add Database Schema

1. Navigate to your project
2. Go to the Schema section
3. Add table schemas in JSON format:

```json
{
  "schemas": [
    {
      "table_name": "users",
      "table_schema": {
        "columns": [
          { "name": "id", "type": "INTEGER", "primary_key": true },
          { "name": "username", "type": "VARCHAR(50)", "unique": true },
          { "name": "email", "type": "VARCHAR(100)", "unique": true }
        ]
      }
    }
  ]
}
```

### 3. Generate SQL Queries

1. Go to the Query section
2. Enter natural language request:
   - "Show me all users who registered in the last 30 days"
   - "Find products with low stock (less than 10 items)"
   - "Get total sales by category"
3. Click "Generate Query"
4. Review the generated SQL and explanation

## 🗂️ Project Structure

```
QueryCraft/
├── server/                 # Flask Backend
│   ├── app/
│   │   ├── models/        # MongoDB models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── utils/         # Utilities
│   │   └── config/        # Configuration
│   ├── requirements.txt   # Python dependencies
│   ├── app.py            # Main application
│   └── README.md         # Backend documentation
├── web/                   # React Frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── store/        # Zustand stores
│   │   ├── lib/          # Utilities and services
│   │   └── types/        # TypeScript interfaces
│   ├── package.json      # Node.js dependencies
│   └── README.md         # Frontend documentation
├── start-app.sh          # Full stack startup script
└── README.md            # This file
```

## 🚀 Deployment

### Backend Deployment

1. Set production environment variables
2. Use Gunicorn or uWSGI
3. Set up MongoDB with authentication
4. Configure reverse proxy (Nginx/Apache)
5. Set up SSL/TLS certificates

### Frontend Deployment

1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or similar
3. Set environment variables
4. Configure API URL for production

## 🧪 Testing

### Backend Testing

```bash
cd server
python test_api.py
```

### Frontend Testing

```bash
cd web
npm run test
```

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based auth
- **Input Validation**: Comprehensive validation
- **SQL Injection Prevention**: Query validation
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Controlled cross-origin requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Review the console logs
3. Ensure all services are running
4. Create an issue in the repository

## 🎉 Acknowledgments

- OpenAI for GPT-3.5-turbo API
- Flask and React communities
- shadcn/ui for beautiful components
- All contributors and users
