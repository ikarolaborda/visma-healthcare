# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FHIR R4-compliant Healthcare Patient Management System with Django REST Framework backend and Vue 3 frontend. The system manages patients, practitioners, appointments, prescriptions, clinical records, and billing with full FHIR resource compliance.

## Common Development Commands

### Docker & Services
```bash
# Build and start all services
make build && make up

# Complete installation (recommended for first setup)
make install  # Builds, migrates, creates demo user (demo/demo123), seeds data

# View logs
make logs              # All services
make logs-backend      # Backend only
make logs-frontend     # Frontend only

# Stop services
make down

# Check service status
make status
```

### Backend Development
```bash
# Run backend tests
make test
docker compose exec backend pytest -v

# Run specific test file
docker compose exec backend pytest patients/tests/test_api.py -v

# Run specific test class/method
docker compose exec backend pytest patients/tests/test_models.py::TestPatientModel -v

# Test with coverage
make test-coverage

# Database migrations
make migrate                    # Apply migrations
make makemigrations            # Create new migrations
make shell                     # Django shell
make dbshell                   # PostgreSQL shell

# Code quality
make lint                      # Run black, flake8, isort checks
make format                    # Auto-format with black and isort

# Create superuser
make createsuperuser

# Seed database
make seed                      # 50 diverse patients
make seed-all                  # All entities (patients, practitioners, appointments, etc.)
make seed-scenarios            # Test scenarios
```

### Frontend Development
```bash
# Frontend runs in Docker container on port 80
# For local development outside Docker:
cd frontend
npm install
npm run dev                    # Dev server with hot reload
npm run build                  # Production build
npm run type-check             # TypeScript type checking
npm run lint                   # ESLint
```

## Architecture Overview

### Backend Architecture (Django REST Framework)

**Multi-app FHIR-compliant structure:**
- `patients/` - Patient FHIR resources (core)
- `practitioners/` - Practitioner FHIR resources
- `appointments/` - Appointment FHIR resources
- `prescriptions/` - MedicationRequest FHIR resources
- `patient_history/` - Clinical records
- `billing/` - Invoice management
- `authentication/` - JWT auth (register, login, token refresh)
- `common/` - Shared utilities and base classes
- `config/` - Django settings and root URL configuration

**FHIR Serializer Pattern:**
Each FHIR app uses dual serializers:
1. Standard DRF serializer (e.g., `PatientSerializer`) - for internal Django operations
2. FHIR serializer (e.g., `FHIRPatientSerializer`) - converts to/from FHIR R4 format
   - `to_representation()` - Django model → FHIR resource
   - `to_internal_value()` - FHIR resource → Django model data
   - Uses `fhir.resources` library for validation

**Key Backend Files:**
- `backend/config/settings.py` - Django settings with JWT, CORS, Redis cache, Celery config
- `backend/config/urls.py` - Root URL routing (auth, FHIR endpoints, Swagger)
- `backend/*/serializers.py` - FHIR serialization logic
- `backend/*/models.py` - Django models with FHIR field mappings
- `backend/*/views.py` - DRF viewsets (typically ModelViewSet)
- `backend/pytest.ini` - Test configuration

**Authentication:**
- JWT tokens via `djangorestframework-simplejwt`
- Access tokens: 1 hour lifetime
- Refresh tokens: 1 day lifetime
- Token blacklist on logout
- All FHIR endpoints require authentication (Bearer token)

**Infrastructure Services:**
- PostgreSQL 16 - primary database
- Redis - caching layer
- RabbitMQ - message broker for Celery
- Celery Worker - async task processing
- Celery Beat - periodic task scheduler

### Frontend Architecture (Vue 3 + TypeScript)

**State Management:**
- Pinia stores for state (auth, patient, practitioner, appointment, prescription, invoice, clinical record)
- Each store in `frontend/src/stores/` handles CRUD operations and API calls

**API Service Layer:**
- `frontend/src/services/api.ts` - Axios instance with JWT interceptors
- Individual service files (e.g., `patient.ts`, `practitioner.ts`) - API endpoints
- Services return FHIR-compliant resources from backend

**Routing:**
- `frontend/src/router/index.ts` - Vue Router with authentication guards
- Routes use `requiresAuth: true` meta to enforce authentication
- Navigation guards check token and redirect to login if needed

**Key Frontend Patterns:**
- Composition API for all components
- TypeScript for type safety
- Axios interceptors automatically inject JWT tokens
- Auth store initializes on app load to restore user session
- i18n support (English/Spanish in `frontend/src/locales/`)

**Views Structure:**
- Dashboard - main landing page with stats
- List views - table display with search/filter
- Form views - create/edit (reused for both operations)
- Detail views - display single resource

### Testing Strategy

**Backend Tests (pytest + pytest-django):**
- `test_models.py` - Model validation and methods
- `test_serializers.py` - FHIR serialization/deserialization
- `test_api.py` - API endpoint integration tests
- `test_workflows.py` - End-to-end user workflows
- `test_factories.py` - Factory functionality
- `conftest.py` - Shared fixtures

**Test Fixtures:**
- Use `factory-boy` factories for test data generation
- Faker integration for realistic data
- API client fixture with authentication helper

**Coverage:**
pytest.ini configures coverage to generate HTML reports in `backend/htmlcov/`

### Docker Architecture

**Multi-stage builds:**
- Backend: Python slim → production with gunicorn
- Frontend: Node build stage → nginx production stage

**Services:**
- `db` - PostgreSQL with health checks
- `redis` - Cache backend with persistence
- `rabbitmq` - Message broker with management UI (port 15672)
- `backend` - Django with gunicorn (4 workers)
- `frontend` - Nginx serving built Vue app
- `celery_worker` - Async task processor
- `celery_beat` - Periodic task scheduler

**Networking:**
All services on `healthcare_network` bridge network for inter-container communication.

## API Endpoints

**Authentication:** `/api/auth/`
- `POST /register/` - Register new user
- `POST /login/` - Login (returns access + refresh tokens)
- `POST /token/refresh/` - Refresh access token
- `GET /profile/` - Get user profile (requires auth)
- `POST /logout/` - Logout and blacklist token

**FHIR Resources:** `/fhir/`
All FHIR endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- `Patient` - `/fhir/Patient/` (GET list, POST create, GET/PUT/DELETE by ID)
- `Practitioner` - `/fhir/Practitioner/`
- `Appointment` - `/fhir/Appointment/`
- `MedicationRequest` - `/fhir/MedicationRequest/` (prescriptions)
- `ClinicalRecord` - `/fhir/ClinicalRecord/` (patient history)
- `Invoice` - `/fhir/Invoice/` (billing)

**Documentation:**
- `/swagger/` - Interactive Swagger UI with auth support
- `/redoc/` - ReDoc documentation

## FHIR Compliance Notes

- All patient data uses FHIR R4 resource structure
- HumanName with `use`, `family`, `given` fields
- Address with `use`, `line`, `city`, `state`, `postalCode`, `country`
- ContactPoint (telecom) for email/phone with `system`, `value`, `use`
- All resources have `resourceType`, `id`, and resource-specific fields
- Use `fhir.resources` library for validation and structure

## Environment Configuration

**.env file** (copy from `.env.example`):
- `DEBUG` - Django debug mode (default: True)
- `SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - PostgreSQL config
- `REDIS_URL` - Redis connection URL
- `CELERY_BROKER_URL` - RabbitMQ URL for Celery
- `CORS_ALLOWED_ORIGINS` - Comma-separated allowed origins

## Port Mapping

- Frontend: http://localhost (port 80)
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- RabbitMQ AMQP: localhost:5672
- RabbitMQ Management UI: http://localhost:15672

## Common Tasks

**Adding a new FHIR resource:**
1. Create Django app: `docker compose exec backend python manage.py startapp <app_name>`
2. Define model in `models.py` with FHIR-compliant fields
3. Create dual serializers (standard + FHIR)
4. Create viewset in `views.py` (typically `ModelViewSet`)
5. Add URL routing in `urls.py`
6. Register app in `config/settings.py` INSTALLED_APPS
7. Include URLs in `config/urls.py`
8. Create factories for testing
9. Write tests (models, serializers, API)
10. Run migrations: `make makemigrations && make migrate`

**Modifying FHIR serialization:**
- Edit `to_representation()` for Django → FHIR conversion
- Edit `to_internal_value()` for FHIR → Django conversion
- Ensure FHIR resource validation using `fhir.resources` classes
- Update tests to verify FHIR compliance

**Frontend API integration:**
1. Create TypeScript interface in `frontend/src/types/`
2. Add service methods in `frontend/src/services/`
3. Create/update Pinia store in `frontend/src/stores/`
4. Create views (List, Form, Detail) in `frontend/src/views/`
5. Add routes in `frontend/src/router/index.ts`
6. Update navigation in `App.vue` or layout components
