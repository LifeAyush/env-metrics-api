# Metrics Backend API ![Python](https://img.shields.io/badge/python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green) ![Celery](https://img.shields.io/badge/Celery-5.3.6-%23A0C)

A FastAPI-based REST API for managing environmental metrics with authentication, async processing, and comprehensive error handling.

## Features

- **Authentication & Authorization**: JWT-based authentication with secure password hashing
- **Metrics Management**: CRUD operations for environmental metrics (Energy, Water, Waste)
- **Async Processing**: Celery-based background task processing
- **Comprehensive Logging**: Structured logging throughout the application
- **Error Handling**: Custom exception handling with detailed error responses
- **Database Support**: SQLAlchemy ORM with support for SQLite, PostgreSQL, and MySQL
- **Health Checks**: Built-in health and readiness endpoints
- **Input Validation**: Pydantic-based request/response validation

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd metrics-backend
   ```
2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./test.db

# JWT Configuration (REQUIRED - no default for security)
JWT_SECRET=your-super-secret-jwt-key-here-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENV=development

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Redis Configuration for Celery
REDIS_URL=redis://localhost:6379/0
```

## Running the Application

### Development Mode

1. **Start Redis** (required for Celery)

   ```bash
   redis-server
   ```
2. **Start Celery worker** (in a separate terminal)

   ```bash
   celery -A app.celery_worker worker --loglevel=info
   ```
3. **Start the API server**

   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Authenticate and get access token

### Metrics

- `GET /metrics` - Get metrics with filtering and pagination
- `POST /metrics` - Create a new metric (async)
- `PUT /metrics/{metric_id}` - Update a metric
- `DELETE /metrics/{metric_id}` - Delete a metric
- `GET /metrics/{metric_id}/related` - Get related metrics

### Health Checks

- `GET /health` - Basic health check

## Error Handling

The API uses custom exceptions with consistent error responses:

```json
{
  "error": "Error message",
  "error_code": "ERROR_TYPE",
  "extra_data": {}
}
```

### Error Types

- `AUTH_ERROR` - Authentication failures
- `AUTHORIZATION_ERROR` - Permission issues
- `VALIDATION_ERROR` - Input validation failures
- `NOT_FOUND` - Resource not found
- `DATABASE_ERROR` - Database operation failures
- `EXTERNAL_SERVICE_ERROR` - External service issues

## Logging

The application uses structured logging with configurable levels:

- **DEBUG**: Detailed debugging information
- **INFO**: General application information
- **WARNING**: Warning messages
- **ERROR**: Error messages

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Database

### Supported Databases

- SQLite (development)
- PostgreSQL (production recommended)
- MySQL (production)

### Database Configuration

The application automatically detects the database type and applies appropriate configuration:

- SQLite: Uses `check_same_thread=False`
- PostgreSQL/MySQL: Standard configuration
