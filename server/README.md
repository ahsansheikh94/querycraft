# SQL Query Generator - Flask Backend

A production-ready Flask backend system for generating SQL queries from natural language using OpenAI's GPT models. This application provides a complete API for user authentication, project management, schema management, and AI-powered SQL query generation.

## Features

### 🔐 Authentication System

- User registration and login with JWT tokens
- Password hashing with bcrypt
- Protected routes with middleware
- Token refresh functionality

### 📁 Project Management

- Create, read, update, and delete SQL projects
- User-project associations
- Project statistics and metadata

### 🗄️ Schema Management

- Store and manage database table schemas
- JSON-based schema format
- Schema validation and bulk operations
- Schema summaries and statistics

### 🤖 AI Query Generation

- Natural language to SQL conversion using OpenAI GPT
- Query explanation in plain English
- Query improvement suggestions
- Error handling and rate limiting

### 📊 Query Management

- Query history and search functionality
- Pagination and filtering
- Query statistics and analytics
- Detailed query explanations

## Technology Stack

- **Framework**: Flask 2.3.3
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT with Flask-JWT-Extended
- **AI Integration**: OpenAI GPT-3.5-turbo
- **Validation**: Marshmallow schemas
- **Security**: bcrypt password hashing
- **Rate Limiting**: Flask-Limiter
- **CORS**: Flask-CORS

## Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- OpenAI API key

## Installation

1. **Clone the repository**

   ```bash
   cd server
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp env.example .env
   ```

   Edit `.env` file with your configuration:

   ```env
   MONGODB_URI=mongodb://localhost:27017/sql_query_generator
   SECRET_KEY=your-super-secret-key-change-this-in-production
   JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
   OPENAI_API_KEY=your-openai-api-key-here
   ```

5. **Start MongoDB**

   ```bash
   # If using local MongoDB
   mongod
   ```

6. **Run the application**

   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

## Database Setup

The application automatically creates the necessary collections and indexes when it starts. The database structure includes:

- **users**: User accounts and authentication
- **projects**: SQL projects owned by users
- **schemas**: Table schemas for each project
- **queries**: Generated SQL queries and metadata

## API Endpoints

### Authentication

```
POST /api/auth/register     - User registration
POST /api/auth/login        - User login
GET  /api/auth/me           - Get current user
POST /api/auth/refresh      - Refresh JWT token
PUT  /api/auth/profile      - Update user profile
```

### Projects

```
POST   /api/projects                    - Create project
GET    /api/projects                    - List user projects
GET    /api/projects/{id}              - Get project details
PUT    /api/projects/{id}              - Update project
DELETE /api/projects/{id}              - Delete project
GET    /api/projects/{id}/stats        - Get project statistics
```

### Schemas

```
POST   /api/projects/{id}/schema       - Create/update schemas
GET    /api/projects/{id}/schema       - Get project schemas
PUT    /api/projects/{id}/schema       - Replace all schemas
GET    /api/projects/{id}/schema/{schema_id}  - Get specific schema
PUT    /api/projects/{id}/schema/{schema_id}  - Update specific schema
DELETE /api/projects/{id}/schema/{schema_id}  - Delete specific schema
GET    /api/projects/{id}/schema/summary      - Get schema summary
```

### Queries

```
POST   /api/projects/{id}/query        - Generate SQL query
GET    /api/projects/{id}/queries      - List project queries
GET    /api/queries/{id}               - Get specific query
GET    /api/queries/{id}/explain       - Get detailed explanation
GET    /api/queries/{id}/improve       - Get improvement suggestions
DELETE /api/queries/{id}               - Delete query
GET    /api/projects/{id}/queries/stats - Get query statistics
```

## Usage Examples

### 1. User Registration

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Create Project

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "E-commerce Database",
    "description": "Database for online store"
  }'
```

### 4. Add Schema

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

### 5. Generate SQL Query

```bash
curl -X POST http://localhost:5000/api/projects/PROJECT_ID/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_input": "Show me all users who registered in the last 30 days"
  }'
```

## Schema Format

The application expects schemas in the following JSON format:

```json
{
  "schemas": [
    {
      "table_name": "users",
      "table_schema": {
        "columns": [
          {
            "name": "id",
            "type": "INTEGER",
            "primary_key": true
          },
          {
            "name": "username",
            "type": "VARCHAR(50)",
            "unique": true,
            "not_null": true
          },
          {
            "name": "email",
            "type": "VARCHAR(100)",
            "unique": true,
            "not_null": true
          }
        ]
      }
    }
  ]
}
```

## Seed Data

To populate the database with sample data for testing:

```bash
python seed_data.py
```

This will create:

- A test user (test@example.com / password123)
- A sample e-commerce project
- 5 table schemas (users, products, categories, orders, order_items)
- 3 sample queries

## Configuration

### Environment Variables

| Variable             | Description               | Default                                         |
| -------------------- | ------------------------- | ----------------------------------------------- |
| `MONGODB_URI`        | MongoDB connection string | `mongodb://localhost:27017/sql_query_generator` |
| `SECRET_KEY`         | Flask secret key          | `dev-secret-key-change-in-production`           |
| `JWT_SECRET_KEY`     | JWT signing key           | `jwt-secret-key-change-in-production`           |
| `OPENAI_API_KEY`     | OpenAI API key            | Required                                        |
| `CORS_ORIGINS`       | Allowed CORS origins      | `http://localhost:3000`                         |
| `RATE_LIMIT_DEFAULT` | Default rate limit        | `100/hour`                                      |
| `RATE_LIMIT_AUTH`    | Auth endpoint rate limit  | `10/minute`                                     |

### Rate Limiting

The application implements rate limiting to prevent abuse:

- Authentication endpoints: 10 requests per minute
- Default endpoints: 100 requests per hour
- Custom limits can be configured per endpoint

## Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation using Marshmallow
- **SQL Injection Prevention**: Query validation and sanitization
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Controlled cross-origin requests

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": ["Detailed error messages"]
}
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Running with Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Database Indexes

The application automatically creates the following indexes for optimal performance:

- Users: email (unique), username (unique), created_at
- Projects: user_id, created_at, (user_id, name)
- Schemas: project_id, (project_id, table_name) unique
- Queries: project_id, created_at, (project_id, created_at)

## Testing

To test the API endpoints, you can use tools like:

- **Postman**: Import the collection
- **curl**: Command-line examples provided above
- **Python requests**: For programmatic testing

## Production Deployment

1. **Set production environment variables**
2. **Use a production WSGI server** (Gunicorn, uWSGI)
3. **Set up MongoDB with authentication**
4. **Configure reverse proxy** (Nginx, Apache)
5. **Set up SSL/TLS certificates**
6. **Configure monitoring and logging**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the documentation
2. Review the error logs
3. Create an issue in the repository
