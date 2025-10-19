.PHONY: help build up down restart logs clean test migrate shell createsuperuser collectstatic build-frontend

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Healthcare Patient Management System$(NC)"
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Commands

build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker compose build

up: ## Start all services in detached mode
	@echo "$(GREEN)Starting services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "$(BLUE)Frontend: http://localhost$(NC)"
	@echo "$(BLUE)Backend API: http://localhost:8000$(NC)"
	@echo "$(BLUE)API Docs: http://localhost:8000/swagger/$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker compose down

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker compose logs -f

logs-backend: ## Show logs from backend service only
	docker compose logs -f backend

logs-frontend: ## Show logs from frontend service only
	docker compose logs -f frontend

logs-db: ## Show logs from database service only
	docker compose logs -f db

##@ Database Commands

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	docker compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	@echo "$(GREEN)Creating migrations...$(NC)"
	docker compose exec backend python manage.py makemigrations

createsuperuser: ## Create Django superuser
	@echo "$(GREEN)Creating superuser...$(NC)"
	docker compose exec backend python manage.py createsuperuser

shell: ## Open Django shell
	docker compose exec backend python manage.py shell

dbshell: ## Open PostgreSQL shell
	docker compose exec db psql -U postgres -d healthcare_db

seed: ## Seed database with 50 realistic patients
	@echo "$(GREEN)Seeding database with patients...$(NC)"
	docker compose exec backend python manage.py seed_patients --count 50 --diverse
	@echo "$(GREEN)Database seeded successfully!$(NC)"

seed-scenarios: ## Seed database with test scenarios
	@echo "$(GREEN)Seeding database with test scenarios...$(NC)"
	docker compose exec backend python manage.py seed_patients --scenarios
	@echo "$(GREEN)Test scenarios created!$(NC)"

seed-large: ## Seed database with 200 diverse patients
	@echo "$(GREEN)Seeding database with large patient population...$(NC)"
	docker compose exec backend python manage.py seed_patients --count 200 --diverse
	@echo "$(GREEN)Large dataset created!$(NC)"

seed-clear: ## Clear database and reseed with fresh data
	@echo "$(YELLOW)Clearing and reseeding database...$(NC)"
	docker compose exec backend python manage.py seed_patients --count 50 --diverse --clear
	@echo "$(GREEN)Database cleared and reseeded!$(NC)"

##@ Development Commands

build-frontend: ## Rebuild frontend (clean build with fresh assets)
	@echo "$(YELLOW)Stopping frontend container...$(NC)"
	@docker compose stop frontend
	@echo "$(YELLOW)Removing old frontend container and image...$(NC)"
	@docker compose rm -f frontend
	@docker rmi -f healthcare_patient_management-frontend 2>/dev/null || true
	@echo "$(GREEN)Building fresh frontend image...$(NC)"
	@docker compose build --no-cache frontend
	@echo "$(GREEN)Starting frontend container...$(NC)"
	@docker compose up -d frontend
	@echo ""
	@echo "$(GREEN)✓ Frontend rebuilt successfully!$(NC)"
	@echo "$(BLUE)Frontend available at: http://localhost$(NC)"

collectstatic: ## Collect static files
	@echo "$(GREEN)Collecting static files...$(NC)"
	docker compose exec backend python manage.py collectstatic --noinput

test: ## Run backend tests
	@echo "$(GREEN)Running tests...$(NC)"
	docker compose exec backend pytest -v

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	docker compose exec backend pytest --cov=. --cov-report=html --cov-report=xml --cov-report=term

lint: ## Run code linting
	@echo "$(GREEN)Running linters...$(NC)"
	docker compose exec backend black --check .
	docker compose exec backend flake8 .
	docker compose exec backend isort --check-only .

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	docker compose exec backend black .
	docker compose exec backend isort .

##@ Cleanup Commands

clean: ## Remove all containers, volumes, and images
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker compose down -v --rmi all
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-volumes: ## Remove all volumes (WARNING: This will delete all data!)
	@echo "$(YELLOW)Removing volumes...$(NC)"
	docker compose down -v
	@echo "$(GREEN)Volumes removed!$(NC)"

prune: ## Remove all unused Docker resources
	@echo "$(YELLOW)Pruning Docker resources...$(NC)"
	docker system prune -af --volumes
	@echo "$(GREEN)Prune complete!$(NC)"

##@ Setup Commands

setup: ## Complete setup: build containers, generate swagger, start services, migrate, seed data, and show health status
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Healthcare Patient Management System - Complete Setup    ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Step 1/8: Building Docker containers...$(NC)"
	@docker compose build
	@echo ""
	@echo "$(GREEN)Step 2/8: Starting all containers...$(NC)"
	@docker compose up -d
	@echo ""
	@echo "$(GREEN)Step 3/8: Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo ""
	@echo "$(GREEN)Step 4/8: Running database migrations...$(NC)"
	@docker compose exec backend python manage.py migrate
	@echo ""
	@echo "$(GREEN)Step 5/8: Collecting static files...$(NC)"
	@docker compose exec backend python manage.py collectstatic --noinput
	@echo ""
	@echo "$(GREEN)Step 6/8: Creating demo user account...$(NC)"
	@docker compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com', 'first_name': 'Demo', 'last_name': 'User'}); u.set_password('demo123'); u.save(); print('  ✓ Demo user created' if created else '  ✓ Demo user already exists')"
	@echo "$(YELLOW)  Demo credentials - Username: demo, Password: demo123$(NC)"
	@echo ""
	@echo "$(GREEN)Step 7/8: Seeding all application data...$(NC)"
	@docker compose exec backend python seed_realistic_data.py
	@echo ""
	@echo "$(GREEN)Step 8/8: Checking container health status...$(NC)"
	@echo ""
	@docker compose ps
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║              Setup Complete! 🎉                            ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Application is ready to use!$(NC)"
	@echo ""
	@echo "$(YELLOW)Access Points:$(NC)"
	@echo "  Frontend:        $(BLUE)http://localhost$(NC)"
	@echo "  Backend API:     $(BLUE)http://localhost:8000$(NC)"
	@echo "  API Swagger:     $(BLUE)http://localhost:8000/swagger/$(NC)"
	@echo "  API ReDoc:       $(BLUE)http://localhost:8000/redoc/$(NC)"
	@echo ""
	@echo "$(YELLOW)Demo Login:$(NC)"
	@echo "  Username: $(BLUE)demo$(NC)"
	@echo "  Password: $(BLUE)demo123$(NC)"
	@echo ""

dev-setup: setup ## Alias for complete setup (same as setup)
	@echo "$(GREEN)Development environment ready!$(NC)"

install: ## Complete installation: build, start, migrate, create demo user, and seed all data
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Healthcare Patient Management System - Full Installation ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Step 1/7: Building Docker images...$(NC)"
	@docker compose build
	@echo ""
	@echo "$(GREEN)Step 2/7: Starting services...$(NC)"
	@docker compose up -d
	@echo ""
	@echo "$(GREEN)Step 3/7: Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo ""
	@echo "$(GREEN)Step 4/7: Running database migrations...$(NC)"
	@docker compose exec backend python manage.py migrate
	@echo ""
	@echo "$(GREEN)Step 5/7: Collecting static files...$(NC)"
	@docker compose exec backend python manage.py collectstatic --noinput
	@echo ""
	@echo "$(GREEN)Step 6/7: Creating demo user account...$(NC)"
	@docker compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com', 'first_name': 'Demo', 'last_name': 'User'}); u.set_password('demo123'); u.save(); print('  ✓ Demo user created' if created else '  ✓ Demo user already exists')"
	@echo "$(YELLOW)  Demo credentials - Username: demo, Password: demo123$(NC)"
	@echo ""
	@echo "$(GREEN)Step 7/7: Seeding database with realistic data...$(NC)"
	@docker compose exec backend python seed_realistic_data.py
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║              Installation Complete! 🎉                     ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Application is ready to use!$(NC)"
	@echo ""
	@echo "$(YELLOW)Access the application:$(NC)"
	@echo "  Frontend:        $(BLUE)http://localhost$(NC)"
	@echo "  Backend API:     $(BLUE)http://localhost:8000$(NC)"
	@echo "  API Docs:        $(BLUE)http://localhost:8000/swagger/$(NC)"
	@echo ""
	@echo "$(YELLOW)Demo Login Credentials:$(NC)"
	@echo "  Username: $(BLUE)demo$(NC)"
	@echo "  Password: $(BLUE)demo123$(NC)"
	@echo ""
	@echo "$(YELLOW)Database contains:$(NC)"
	@echo "  • 15 Patients"
	@echo "  • 8 Practitioners"
	@echo "  • 50 Appointments"
	@echo "  • 40 Prescriptions"
	@echo "  • 70 Clinical Records"
	@echo "  • 20 Invoices"
	@echo ""

create-demo-user: ## Create demo user for testing (username: demo, password: demo123)
	@echo "$(GREEN)Creating demo user...$(NC)"
	@docker compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com', 'first_name': 'Demo', 'last_name': 'User'}); u.set_password('demo123'); u.save(); print('✓ Demo user created' if created else '✓ Demo user already exists')"
	@echo "$(YELLOW)Username: demo, Password: demo123$(NC)"

seed-all: ## Seed database with all realistic data (patients, practitioners, appointments, prescriptions, records, invoices)
	@echo "$(GREEN)Seeding all data...$(NC)"
	@docker compose exec backend python seed_realistic_data.py
	@echo "$(GREEN)All data seeded successfully!$(NC)"

##@ Status Commands

status: ## Show status of all services
	docker compose ps

health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(NC)"
	@docker compose ps | grep -q "Up (healthy)" && echo "$(GREEN)✓ All services healthy$(NC)" || echo "$(YELLOW)⚠ Some services may not be healthy$(NC)"

ps: status ## Alias for status

##@ Backup and Restore

backup-db: ## Backup database to backup.sql
	@echo "$(GREEN)Backing up database...$(NC)"
	docker compose exec -T db pg_dump -U postgres healthcare_db > backup.sql
	@echo "$(GREEN)Database backed up to backup.sql$(NC)"

restore-db: ## Restore database from backup.sql
	@echo "$(YELLOW)Restoring database from backup.sql...$(NC)"
	docker compose exec -T db psql -U postgres healthcare_db < backup.sql
	@echo "$(GREEN)Database restored!$(NC)"
