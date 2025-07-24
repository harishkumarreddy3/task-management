# 📋 Task Management Backend (FastAPI)

## 🧭 Overview

A robust FastAPI backend for a task management application with user authentication and CRUD operations for tasks. Built with SQLAlchemy ORM, PostgreSQL database, and JWT-based authentication via HTTP-only cookies.

---

## 🚀 Features

- **🔐 User Authentication**
  - User registration (`POST /auth/`)
  - Secure login with JWT tokens (`POST /auth/token`)
  - Logout functionality (`POST /auth/logout`)
  
- **📋 Task Management**
  - Create tasks (`POST /taskmanager/`)
  - Get specific task (`GET /taskmanager/{task_id}`)
  - List all user tasks (`GET /taskmanager/tasks`)
  - Update tasks (`PUT/PATCH /taskmanager/{task_id}`)
  - Delete tasks (`DELETE /taskmanager/{task_id}`)
  
- **🛡️ Security**
  - bcrypt password hashing
  - JWT tokens in HTTP-only cookies
  - CORS protection
  - Input validation with Pydantic

---

## 🗂️ Project Structure

```
Taskmanager/
├── pyproject.toml          # Project dependencies and metadata
├── uv.lock                 # Dependency lock file
├── README.md
└── src/
    └── taskmanager/
        ├── main.py         # FastAPI application entry point
        ├── controller/     # API route handlers
        │   ├── auth_controller.py
        │   └── task_controller.py
        ├── service/        # Business logic layer
        │   ├── auth_service.py
        │   └── task_service.py
        ├── model/          # SQLAlchemy models
        │   ├── user.py
        │   └── task.py
        ├── database/       # Database configuration
        │   └── db.py
        └── core/           # Core configuration
            ├── config.py
            └── deps.py
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
HOST=localhost
PORT=3510

# Application Settings
APP_NAME=Task Manager API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# Frontend Configuration
FRONTEND_URL=http://localhost:5173

# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5433/postgres

# Authentication
AUTH_SECRET_KEY=your_secret_key_here
AUTH_ALGORITHM=HS256
```

---

## 🧪 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/` | Register new user |
| `POST` | `/auth/token` | Login (returns JWT in cookie) |
| `POST` | `/auth/logout` | Logout (clears JWT cookie) |

### 📋 Task Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/taskmanager/tasks` | Get all user tasks |
| `GET` | `/taskmanager/{task_id}` | Get specific task |
| `POST` | `/taskmanager/` | Create new task |
| `PUT` | `/taskmanager/{task_id}` | Update task (complete) |
| `PATCH` | `/taskmanager/{task_id}` | Update task (partial) |
| `DELETE` | `/taskmanager/{task_id}` | Delete task |

---

## 🏃 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- `uv` package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Taskmanager
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment**
   ```bash
   # Copy and edit the environment file
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the application**
   ```bash
   uv run python -m src.taskmanager.main
   ```

### Alternative Run Commands

```bash
# Using uvicorn directly
uvicorn src.taskmanager.main:app --reload --host localhost --port 3510

# Using Python module
python -m src.taskmanager.main
```

---

## 🌐 Access Points

- **API Base**: http://localhost:3510
- **Interactive Docs**: http://localhost:3510/docs
- **Alternative Docs**: http://localhost:3510/redoc
- **Health Check**: http://localhost:3510/health

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_date TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR NOT NULL,
    description TEXT,
    category VARCHAR NOT NULL,
    priority VARCHAR NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMP,
    created_date TIMESTAMP DEFAULT NOW()
);
```

---

## 🧪 Testing Examples

### Create User
```bash
curl -X POST "http://localhost:3510/auth/" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST "http://localhost:3510/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Create Task
```bash
curl -X POST "http://localhost:3510/taskmanager/" \
  -H "Content-Type: application/json" \
  -H "Cookie: jwt=your_jwt_token" \
  -d '{
    "title": "Complete project",
    "description": "Finish the task management API",
    "category": "work",
    "priority": "high",
    "is_completed": false,
    "due_date": "2024-01-20T18:00:00"
  }'
```

---

## 🛡️ Security Features

- **Password Security**: bcrypt hashing with salt
- **JWT Authentication**: Configurable token expiration
- **Cookie Security**: HTTP-only, secure cookies
- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Pydantic model validation

---

## 🔧 Development

### Project Structure Benefits

- **Modular Design**: Clear separation of concerns
- **Type Safety**: Full type hints throughout
- **Dependency Injection**: FastAPI's dependency system
- **Clean Architecture**: Service layer pattern

### Adding New Features

1. **Models**: Add to `src/taskmanager/model/`
2. **Services**: Add business logic to `src/taskmanager/service/`
3. **Controllers**: Add API endpoints to `src/taskmanager/controller/`
4. **Dependencies**: Update `src/taskmanager/core/deps.py`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Task Management Backend** — Built with ❤️ using FastAPI + PostgreSQL
