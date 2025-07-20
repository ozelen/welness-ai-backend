# Wellness AI Backend

A Django-based backend for the Wellness AI application, featuring health tracking, meal planning, and goal management.

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (managed via pyenv)
- **Docker & Docker Compose** (for databases)
- **uv** (Python package manager)
- **pyenv** (Python version manager)

### One-Command Setup

```bash
cd backend
make fresh-install
```

This will:
- ✅ Set up Python 3.13 with pyenv
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start database services (PostgreSQL, Redis, MongoDB)
- ✅ Apply database migrations
- ✅ Ready to run!

After setup, start the development server:
```bash
make run
```

## 📋 Manual Setup

If you prefer to set up step by step:

### 1. Install Prerequisites

#### Install pyenv (macOS)
```bash
brew install pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

#### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Install Docker
Download from [docker.com](https://www.docker.com/products/docker-desktop/)

### 2. Setup Python Environment
```bash
cd backend
make pyenv-setup    # Installs Python 3.13
make install        # Creates venv and installs dependencies
```

### 3. Start Database Services
```bash
make docker-up      # Starts PostgreSQL, Redis, MongoDB
```

### 4. Setup Database
```bash
make migrate        # Apply migrations
```

### 5. Run Development Server
```bash
make run            # Start Django server
```

## 🛠️ Available Commands

### Environment Management
```bash
make help              # Show all available commands
make fresh-install     # Complete fresh environment setup
make install           # Install dependencies
make clean             # Clean environment and cache files
make venv              # Create virtual environment
make venv-check        # Check if virtual environment is active
```

### Django Commands
```bash
make run               # Start Django development server
make run-dev           # Start server with debug output
make migrate           # Apply database migrations
make makemigrations    # Create new migrations
make shell             # Open Django shell
make superuser         # Create Django superuser
make test              # Run tests
make test-coverage     # Run tests with coverage
make check             # Run Django system check
make collectstatic     # Collect static files
```

### Database Management
```bash
make docker-up         # Start database services
make docker-down       # Stop database services
make docker-logs       # Show Docker logs
make docker-restart    # Restart Docker services
make reset-db          # Reset database (with confirmation)
```

### Development Workflow
```bash
make setup-dev         # Setup development environment
make start             # Quick start (setup + run)
```

## 🏗️ Project Structure

```
backend/
├── apps/                  # Django project root
│   ├── apps/             # Main Django project
│   ├── bots/             # Telegram bot app
│   ├── facts/            # Health facts app
│   ├── goals/            # Goal tracking app
│   ├── meals/            # Meal planning app
│   └── manage.py         # Django management script
├── postgres/             # PostgreSQL configuration
├── init-scripts/         # Database initialization scripts
├── docker-compose.yaml   # Docker services configuration
├── pyproject.toml        # Project dependencies
├── Makefile             # Development commands
└── README.md            # This file
```

## 🗄️ Database Services

The project uses Docker Compose to run multiple database services:

- **PostgreSQL** (port 5432) - Main application database
- **Redis** (port 6379) - Caching and session storage
- **MongoDB** (port 27017) - Document storage
- **Mongo Express** (port 8081) - MongoDB web interface

### Database URLs
- PostgreSQL: `postgresql://postgres:postgres@localhost:5432/postgres`
- Redis: `redis://localhost:6379`
- MongoDB: `mongodb://localhost:27017`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

### Django Settings
Main settings are in `apps/apps/settings.py`. Key configurations:

- Database connections
- Installed apps
- Middleware
- Static files
- Templates

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific app tests
cd apps && uv run manage.py test apps.bots
```

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure environment variables
5. Run migrations: `make migrate`
6. Collect static files: `make collectstatic`

### Docker Production
```bash
# Build production image
docker build -t wellness-ai-backend .

# Run with production settings
docker run -p 8000:8000 wellness-ai-backend
```

## 🔍 Troubleshooting

### Common Issues

#### Python Version Issues
```bash
make python-check      # Check Python version compatibility
make pyenv-setup       # Reinstall Python version
```

#### Database Connection Issues
```bash
make docker-logs       # Check database logs
make docker-restart    # Restart database services
```

#### Dependency Issues
```bash
make clean             # Clean environment
make fresh-install     # Fresh setup
```

#### Virtual Environment Issues
```bash
make venv-check        # Check if venv is active
make venv-create       # Recreate virtual environment
```

### Reset Everything
```bash
make clean             # Clean environment
make docker-down       # Stop all services
make fresh-install     # Complete fresh setup
```

## 📚 API Documentation

### Available Endpoints

#### Goals App
- `GET /goals/` - List user goals
- `POST /goals/` - Create new goal
- `GET /goals/{id}/` - Get goal details
- `PUT /goals/{id}/` - Update goal
- `DELETE /goals/{id}/` - Delete goal

#### Meals App
- `GET /meals/` - List meals
- `POST /meals/` - Create meal
- `GET /meals/{id}/` - Get meal details

#### Facts App
- `GET /facts/` - Get health facts
- `POST /facts/` - Create new fact

### Authentication
The API uses Django's built-in authentication system. Include authentication headers in requests:

```bash
curl -H "Authorization: Token your-token-here" http://localhost:8000/api/goals/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Run `make help` to see all available commands
3. Check the logs: `make docker-logs`
4. Create an issue in the repository

## 🔗 Related Projects

- **Frontend**: Flutter mobile app
- **Telegram Bot**: Health tracking bot
- **API Documentation**: Swagger/OpenAPI docs

---

**Happy coding! 🎉**
