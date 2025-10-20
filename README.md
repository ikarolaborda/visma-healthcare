# Healthcare Patient Management System

A FHIR-compliant RESTful API and web application for managing patient information in a healthcare setting, built with Django REST Framework and Vue.js.

## Features

- **FHIR R4 Compliance**: Full adherence to Fast Healthcare Interoperability Resources standard
- **RESTful API**: Complete CRUD operations for patient resources
- **Modern Frontend**: Responsive Vue 3 web interface with Composition API
- **Secure**: JWT authentication and authorization
- **Well-Tested**: Comprehensive unit and integration tests
- **Production-Ready**: Docker containerization with multi-stage builds
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Best Practices**: SOLID principles, clean architecture, and security best practices

## Tech Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL 16
- **FHIR**: fhir.resources library for FHIR R4 compliance
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Docs**: drf-yasg (Swagger/OpenAPI)
- **Server**: Gunicorn
- **Testing**: pytest + pytest-django

### Frontend
- **Framework**: Vue 3 with Composition API
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Server**: Nginx

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Automation**: Makefile

## Project Structure

```
visma-healthcare/
├── backend/                    # Django backend application
│   ├── config/                # Django project settings
│   ├── patients/              # Patient app (FHIR resources)
│   │   ├── models.py         # FHIR-compliant Patient model
│   │   ├── serializers.py    # FHIR serializers
│   │   ├── views.py          # API viewsets
│   │   ├── urls.py           # URL routing
│   │   ├── admin.py          # Django admin configuration
│   │   ├── factories.py      # Test data factories
│   │   └── tests/            # Unit and integration tests
│   ├── authentication/        # Authentication app
│   │   ├── views.py          # Auth views (register, login, profile)
│   │   ├── serializers.py    # User serializers
│   │   └── urls.py           # Auth URL routing
│   ├── Dockerfile            # Multi-stage backend Dockerfile
│   ├── requirements.txt      # Python dependencies
│   ├── manage.py             # Django management script
│   └── pytest.ini            # Pytest configuration
├── frontend/                  # Vue.js frontend application
│   ├── src/
│   │   ├── components/       # Reusable Vue components
│   │   ├── views/            # Page components
│   │   │   ├── PatientList.vue
│   │   │   ├── PatientForm.vue
│   │   │   └── PatientDetail.vue
│   │   ├── services/         # API service layer
│   │   ├── stores/           # Pinia state management
│   │   ├── router/           # Vue Router configuration
│   │   ├── assets/           # CSS and static assets
│   │   ├── App.vue           # Root component
│   │   └── main.js           # Application entry point
│   ├── Dockerfile            # Multi-stage frontend Dockerfile
│   ├── nginx.conf            # Nginx configuration
│   ├── vite.config.js        # Vite configuration
│   ├── package.json          # Node dependencies
│   └── index.html            # HTML entry point
├── docker-compose.yml         # Docker Compose configuration
├── Makefile                   # Development automation
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user account |
| POST | `/api/auth/login/` | Login and obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/token/verify/` | Verify token validity |
| GET | `/api/auth/profile/` | Get user profile (requires auth) |
| POST | `/api/auth/change-password/` | Change password (requires auth) |
| POST | `/api/auth/logout/` | Logout and blacklist token (requires auth) |

### FHIR Patient Endpoints

All patient endpoints require JWT authentication via Bearer token.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/fhir/Patient/` | List all patients (FHIR Bundle) |
| POST | `/fhir/Patient/` | Create a new patient |
| GET | `/fhir/Patient/{id}/` | Retrieve a specific patient |
| PUT | `/fhir/Patient/{id}/` | Update a specific patient |
| DELETE | `/fhir/Patient/{id}/` | Delete a specific patient |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs/` | Interactive API documentation with authentication support |
| GET | `/api/redoc/` | ReDoc API documentation |

## FHIR Patient Resource

The Patient model conforms to FHIR R4 Patient resource structure:

```json
{
  "resourceType": "Patient",
  "id": "uuid",
  "active": true,
  "name": [{
    "use": "official",
    "family": "Doe",
    "given": ["John", "Michael"]
  }],
  "gender": "male",
  "birthDate": "1990-01-01",
  "address": [{
    "use": "home",
    "line": ["123 Main St"],
    "city": "New York",
    "state": "NY",
    "postalCode": "10001",
    "country": "USA"
  }],
  "telecom": [
    {
      "system": "email",
      "value": "john.doe@example.com",
      "use": "home"
    },
    {
      "system": "phone",
      "value": "+1-555-123-4567",
      "use": "home"
    }
  ]
}
```

## Quick Start

### Option 1: Vagrant VM (Recommended - Isolated Environment)

**Perfect for development without affecting your host system!**

1. **Install prerequisites**:
   - [Vagrant](https://www.vagrantup.com/downloads)
   - [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. **Clone and deploy**:
   ```bash
   git clone https://github.com/ikarolaborda/visma-healthcare.git
   cd visma-healthcare
   ./vagrant-deploy.sh up
   ```

3. **Access the application**:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8080/api/
   - Admin: http://localhost:8080/admin/
   - Direct VM: http://192.168.56.10

4. **Manage the VM**:
   ```bash
   ./vagrant-deploy.sh ssh      # SSH into VM
   ./vagrant-deploy.sh logs     # View logs
   ./vagrant-deploy.sh halt     # Stop VM
   ./vagrant-deploy.sh destroy  # Delete VM
   ```

**Benefits**:
- ✅ Completely isolated from your host system
- ✅ No permission conflicts
- ✅ Clean development environment
- ✅ Easy to destroy and recreate
- ✅ Matches production environment closely

---

### Option 2: Docker (Quick and Portable)

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### One-Command Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ikarolaborda/visma-healthcare.git
   cd visma-healthcare
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the complete installation**:
   ```bash
   make install
   ```

   This single command will:
   - ✓ Build all Docker images
   - ✓ Start all services
   - ✓ Run database migrations
   - ✓ Collect static files
   - ✓ Create a demo user account (username: `demo`, password: `demo123`)
   - ✓ Seed the database with realistic data:
     - 15 Patients
     - 8 Practitioners
     - 50 Appointments
     - 40 Prescriptions
     - 70 Clinical Records
     - 20 Invoices

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs/
   - Django Admin: http://localhost:8000/admin/

5. **Login with demo credentials**:
   - **Username**: `demo`
   - **Password**: `demo123`

### Manual Setup (Alternative)

If you prefer to set up manually:

1. **Start the application**:
   ```bash
   make setup
   ```

   Or manually:
   ```bash
   docker compose build
   docker compose up -d
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --noinput
   ```

2. **Create a demo user**:
   ```bash
   make create-demo-user
   ```

3. **Seed the database with all data**:
   ```bash
   make seed-all
   ```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All Patient API endpoints require authentication.

### Getting Started with Authentication

1. **Register a new user**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "password": "SecurePass123",
       "password_confirm": "SecurePass123",
       "first_name": "John",
       "last_name": "Doe"
     }'
   ```

2. **Login and get tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "password": "SecurePass123"
     }'
   ```

   Response:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```

3. **Use the access token in API requests**:
   ```bash
   curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8000/fhir/Patient/
   ```

4. **Refresh expired access tokens**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/token/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"refresh": "<refresh_token>"}'
   ```

### Token Lifetimes

- **Access Token**: 1 hour (for API requests)
- **Refresh Token**: 1 day (for obtaining new access tokens)

### Using Postman

Import the provided Postman collection and environment:
- **Collection**: `.build-artifacts/Healthcare_Patient_Management_API.postman_collection.json`
- **Environment**: `.build-artifacts/Healthcare_Local_Environment.postman_environment.json`

The collection includes:
- Automatic token storage in environment variables
- Pre-configured authentication for all endpoints
- Sample requests for all authentication and FHIR endpoints

### Using Swagger UI

1. Open http://localhost:8000/api/docs/
2. Click "Authorize" button at the top right
3. Enter your token in the format: `Bearer <access_token>`
4. Click "Authorize" to save
5. All requests will now include the authentication token

## Makefile Commands

The project includes a comprehensive Makefile for common operations:

### Docker Commands
- `make build` - Build all Docker images
- `make up` - Start all services
- `make down` - Stop all services
- `make restart` - Restart all services
- `make logs` - Show logs from all services
- `make status` - Show status of all services

### Database Commands
- `make migrate` - Run database migrations
- `make makemigrations` - Create new migrations
- `make createsuperuser` - Create Django superuser
- `make shell` - Open Django shell
- `make dbshell` - Open PostgreSQL shell
- `make seed` - Seed database with 50 realistic patients
- `make seed-scenarios` - Create test scenario patients
- `make seed-large` - Seed with 200 patients
- `make seed-clear` - Clear and reseed database

### Development Commands
- `make test` - Run backend tests
- `make test-coverage` - Run tests with coverage report
- `make lint` - Run code linting
- `make format` - Format code with black and isort
- `make collectstatic` - Collect static files

### Cleanup Commands
- `make clean` - Remove all containers, volumes, and images
- `make clean-volumes` - Remove all volumes (deletes data!)
- `make prune` - Remove all unused Docker resources

### Setup Commands
- `make install` - **Complete installation: build, start, migrate, create demo user, and seed all data (RECOMMENDED)**
- `make setup` - Initial setup: build, start, migrate (without seeding)
- `make dev-setup` - Complete development setup including superuser
- `make create-demo-user` - Create demo user for testing (username: demo, password: demo123)
- `make seed-all` - Seed database with all realistic data (all entities)

### Backup Commands
- `make backup-db` - Backup database to backup.sql
- `make restore-db` - Restore database from backup.sql

## Development

### Data Seeding

The project includes a comprehensive data seeding system for generating realistic test data:

```bash
# Seed with 50 diverse patients
make seed

# Seed with test scenarios
make seed-scenarios

# Seed with 200 patients for performance testing
make seed-large

# Clear database and reseed
make seed-clear
```

See [DATA_SEEDING_GUIDE.md](DATA_SEEDING_GUIDE.md) for detailed documentation on:
- Using factories in tests
- Creating custom patient populations
- Age-specific patient generation
- Test scenario creation

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test file
docker compose exec backend pytest patients/tests/test_models.py -v
```

The test suite includes:
- **test_factories.py**: Factory functionality and data generation
- **test_serializers.py**: FHIR serialization/deserialization
- **test_workflows.py**: End-to-end user workflows
- **test_api.py**: API endpoint integration tests
- **test_api_enhanced.py**: Realistic data API tests

### Code Quality

```bash
# Check code style
make lint

# Format code
make format
```

### Database Management

```bash
# Create new migrations
make makemigrations

# Apply migrations
make migrate

# Open Django shell
make shell

# Open database shell
make dbshell
```

## Architecture and Design

### SOLID Principles

The codebase follows SOLID principles:

1. **Single Responsibility**: Each class/module has one clear purpose
   - Models handle data structure
   - Serializers handle FHIR conversion
   - Views handle HTTP requests
   - Services handle business logic

2. **Open/Closed**: Code is open for extension, closed for modification
   - Use of abstract base classes
   - Extensible through inheritance

3. **Liskov Substitution**: Proper use of inheritance hierarchies
   - DRF ViewSets and Serializers properly extended

4. **Interface Segregation**: Focused interfaces
   - Separate serializers for different use cases
   - Minimal API surface

5. **Dependency Inversion**: Depend on abstractions
   - Use of Django's ORM abstraction
   - Service layer separates business logic

### Security Features

- **Authentication**: JWT-based authentication with token blacklisting
  - Access tokens expire after 1 hour
  - Refresh tokens expire after 1 day
  - Secure password validation (minimum 8 characters, complexity requirements)
  - Token blacklisting on logout for enhanced security
- **Authorization**: Permission-based access control
  - All Patient API endpoints require authentication
  - Role-based access through Django permissions
- **Input Validation**: FHIR schema validation
- **SQL Injection Prevention**: ORM-based queries
- **XSS Protection**: Framework-level protection
- **CORS**: Configurable CORS headers
- **Secure Headers**: Security headers in Nginx
- **Non-root Containers**: Docker containers run as non-root users
- **Password Hashing**: PBKDF2 algorithm with SHA256 hash

### Docker Best Practices

- **Multi-stage builds**: Minimize image size
- **Layer caching**: Optimized build performance
- **Security**: Non-root users, minimal base images
- **Health checks**: Container health monitoring
- **Volume management**: Persistent data storage
- **Network isolation**: Separate Docker network

## Deployment

### Cloud Deployment

The application is ready for deployment on major cloud platforms:

#### AWS Deployment
```bash
# Build and push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag healthcare_backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/healthcare-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/healthcare-backend:latest

# Deploy using ECS, EKS, or Elastic Beanstalk
```

#### GCP Deployment
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/healthcare-backend
gcloud run deploy healthcare-backend --image gcr.io/PROJECT_ID/healthcare-backend --platform managed
```

#### Heroku Deployment
```bash
heroku container:push web -a healthcare-backend
heroku container:release web -a healthcare-backend
```

### Environment Variables

Required environment variables for production:

```env
# Django
DEBUG=False
SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=<strong-password>
DB_HOST=<db-host>
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## Testing

The project includes comprehensive tests:

### Backend Tests
- **Unit Tests**: Test individual models and serializers
- **Integration Tests**: Test API endpoints end-to-end
- **Coverage**: >80% code coverage

### Running Tests

```bash
# All tests
make test

# With coverage report
make test-coverage

# Specific test file
docker compose exec backend pytest patients/tests/test_api.py -v

# Specific test class
docker compose exec backend pytest patients/tests/test_models.py::TestPatientModel -v

# Specific test method
docker compose exec backend pytest patients/tests/test_api.py::TestPatientCreateEndpoint::test_create_patient_success -v
```

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

The documentation includes:
- All available endpoints
- Request/response schemas
- FHIR resource examples
- Authentication requirements
- Try-it-out functionality

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change ports in docker-compose.yml or stop conflicting services
   sudo lsof -i :8000  # Find process using port
   ```

2. **Database connection errors**:
   ```bash
   # Ensure database is healthy
   make status
   # Check database logs
   make logs-db
   ```

3. **Migration errors**:
   ```bash
   # Reset database (WARNING: deletes all data)
   make clean-volumes
   make setup
   ```

4. **Permission errors**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the development team

## Acknowledgments

- FHIR specification: https://www.hl7.org/fhir/
- Django REST Framework: https://www.django-rest-framework.org/
- Vue.js: https://vuejs.org/
