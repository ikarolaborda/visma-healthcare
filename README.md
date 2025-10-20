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

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### One-Command Installation (Recommended)

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

## Alternative Setup (Without Docker)

If Docker is unavailable or you prefer a different setup method, you can run the Healthcare Patient Management System using local installation or alternative containerization technologies.

### Option 1: Local Installation (Native)

This approach runs all services directly on your host operating system.

#### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 20.x or higher
- **PostgreSQL**: 16.x
- **Redis**: 7.x
- **RabbitMQ**: 3.x
- **Git**: For cloning the repository

#### Ubuntu/Debian Setup

1. **Install System Dependencies**:
   ```bash
   # Update package index
   sudo apt update

   # Install Python 3.11+
   sudo apt install -y python3.11 python3.11-venv python3-pip

   # Install PostgreSQL 16
   sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
   wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
   sudo apt update
   sudo apt install -y postgresql-16 postgresql-contrib-16

   # Install Redis
   sudo apt install -y redis-server

   # Install RabbitMQ
   sudo apt install -y rabbitmq-server

   # Install Node.js 22.x
   curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

2. **Configure PostgreSQL**:
   ```bash
   # Start PostgreSQL
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

   # Create database and user
   sudo -u postgres psql << EOF
   CREATE DATABASE healthcare_db;
   CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE healthcare_user SET client_encoding TO 'utf8';
   ALTER ROLE healthcare_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE healthcare_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
   \c healthcare_db
   GRANT ALL ON SCHEMA public TO healthcare_user;
   EOF
   ```

3. **Configure Redis**:
   ```bash
   # Start Redis
   sudo systemctl start redis-server
   sudo systemctl enable redis-server

   # Verify Redis is running
   redis-cli ping  # Should return "PONG"
   ```

4. **Configure RabbitMQ**:
   ```bash
   # Start RabbitMQ
   sudo systemctl start rabbitmq-server
   sudo systemctl enable rabbitmq-server

   # Enable management plugin (optional, for web UI)
   sudo rabbitmq-plugins enable rabbitmq_management

   # Create RabbitMQ user (optional, for security)
   sudo rabbitmqctl add_user healthcare_user your_rabbitmq_password
   sudo rabbitmqctl set_permissions -p / healthcare_user ".*" ".*" ".*"
   ```

5. **Clone and Setup Backend**:
   ```bash
   # Clone repository
   git clone https://github.com/ikarolaborda/visma-healthcare.git
   cd visma-healthcare

   # Create and activate Python virtual environment
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Configure Environment Variables**:
   ```bash
   # Create .env file in project root
   cd /var/www/visma-healthcare
   cat > .env << EOF
   # Django Settings
   DEBUG=True
   SECRET_KEY=your-secret-key-change-in-production
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_NAME=healthcare_db
   DB_USER=healthcare_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # RabbitMQ
   CELERY_BROKER_URL=amqp://healthcare_user:your_rabbitmq_password@localhost:5672//
   CELERY_RESULT_BACKEND=redis://localhost:6379/1

   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
   OPENAI_API_KEY=
   EOF
   ```

7. **Initialize Backend**:
   ```bash
   cd backend
   source venv/bin/activate

   # Run migrations
   python manage.py migrate

   # Collect static files
   python manage.py collectstatic --noinput

   # Create superuser (optional)
   python manage.py createsuperuser

   # Or create demo user
   python manage.py shell << EOF
   from django.contrib.auth.models import User
   if not User.objects.filter(username='demo').exists():
       User.objects.create_user('demo', 'demo@example.com', 'demo123')
       print('Demo user created')
   EOF

   # Seed database (optional)
   python seed_realistic_data.py
   ```

8. **Setup Frontend**:
   ```bash
   cd ../frontend

   # Install dependencies
   npm install

   # Build for production
   npm run build

   # Or run development server
   npm run dev
   ```

9. **Run All Services**:

   You'll need to run multiple processes. Use separate terminal windows or a process manager:

   **Terminal 1 - Django Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

   **Terminal 2 - Celery Worker**:
   ```bash
   cd backend
   source venv/bin/activate
   celery -A config worker -l info
   ```

   **Terminal 3 - Celery Beat**:
   ```bash
   cd backend
   source venv/bin/activate
   celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

   **Terminal 4 - Frontend** (if using dev server):
   ```bash
   cd frontend
   npm run dev
   ```

   **Alternative: Using tmux or screen**:
   ```bash
   # Install tmux
   sudo apt install tmux

   # Create tmux session
   tmux new -s healthcare

   # Split into panes (Ctrl+B then %)
   # Run each service in a separate pane
   ```

10. **Access the Application**:
    - Frontend (dev): http://localhost:5173
    - Backend API: http://localhost:8000
    - API Documentation: http://localhost:8000/api/docs/
    - Django Admin: http://localhost:8000/admin/
    - RabbitMQ Management: http://localhost:15672 (guest/guest)

#### macOS Setup

1. **Install Homebrew** (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Dependencies**:
   ```bash
   # Install Python
   brew install python@3.11

   # Install PostgreSQL
   brew install postgresql@16

   # Install Redis
   brew install redis

   # Install RabbitMQ
   brew install rabbitmq

   # Install Node.js
   brew install node@18
   ```

3. **Start Services**:
   ```bash
   # Start PostgreSQL
   brew services start postgresql@16

   # Start Redis
   brew services start redis

   # Start RabbitMQ
   brew services start rabbitmq
   ```

4. **Create Database**:
   ```bash
   createdb healthcare_db
   psql healthcare_db << EOF
   CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
   \c healthcare_db
   GRANT ALL ON SCHEMA public TO healthcare_user;
   EOF
   ```

5. **Follow steps 5-10 from Ubuntu/Debian setup** for backend, frontend, and running services.

#### Windows Setup

1. **Install Python 3.11+**:
   - Download from: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install PostgreSQL 16**:
   - Download from: https://www.postgresql.org/download/windows/
   - Run installer and note the password you set for the postgres user

3. **Install Redis**:
   - Download from: https://github.com/microsoftarchive/redis/releases
   - Or use Windows Subsystem for Linux (WSL)

4. **Install RabbitMQ**:
   - Install Erlang first: https://www.erlang.org/downloads
   - Download RabbitMQ: https://www.rabbitmq.com/install-windows.html

5. **Install Node.js 18.x**:
   - Download from: https://nodejs.org/

6. **Create Database**:
   ```cmd
   # Open PostgreSQL SQL Shell (psql)
   CREATE DATABASE healthcare_db;
   CREATE USER healthcare_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;
   ```

7. **Setup Project**:
   ```cmd
   # Clone repository
   git clone https://github.com/ikarolaborda/visma-healthcare.git
   cd visma-healthcare

   # Setup backend
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

   # Run migrations
   python manage.py migrate
   python manage.py collectstatic --noinput

   # Setup frontend
   cd ..\frontend
   npm install
   npm run build
   ```

8. **Run services** in separate Command Prompt windows as described in step 9 of Ubuntu setup.

#### Using Process Managers (Production)

For production deployments on native systems, use a process manager:

**Systemd (Linux)**:

Create service files in `/etc/systemd/system/`:

```ini
# /etc/systemd/system/healthcare-backend.service
[Unit]
Description=Healthcare Django Backend
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/visma-healthcare/backend
Environment="PATH=/var/www/visma-healthcare/backend/venv/bin"
EnvironmentFile=/var/www/visma-healthcare/.env
ExecStart=/var/www/visma-healthcare/backend/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable healthcare-backend
sudo systemctl start healthcare-backend
```

**Supervisor (Cross-platform)**:
```bash
# Install supervisor
sudo apt install supervisor  # Ubuntu/Debian
brew install supervisor      # macOS

# Create config file
sudo nano /etc/supervisor/conf.d/healthcare.conf
```

```ini
[program:healthcare-backend]
command=/var/www/visma-healthcare/backend/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
directory=/var/www/visma-healthcare/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/healthcare/backend.log

[program:healthcare-celery-worker]
command=/var/www/visma-healthcare/backend/venv/bin/celery -A config worker -l info
directory=/var/www/visma-healthcare/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/healthcare/celery-worker.log

[program:healthcare-celery-beat]
command=/var/www/visma-healthcare/backend/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/var/www/visma-healthcare/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/healthcare/celery-beat.log
```

Start services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Option 2: Podman (Docker Alternative)

Podman is a daemonless container engine that's compatible with Docker commands and Docker Compose files.

#### Install Podman

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install -y podman podman-compose
```

**macOS**:
```bash
brew install podman podman-compose
```

**Fedora/RHEL**:
```bash
sudo dnf install -y podman podman-compose
```

#### Run the Application

```bash
# Clone repository
git clone https://github.com/ikarolaborda/visma-healthcare.git
cd visma-healthcare

# Copy environment file
cp .env.example .env

# Build and start with podman-compose
podman-compose build
podman-compose up -d

# Run migrations
podman-compose exec backend python manage.py migrate
podman-compose exec backend python manage.py collectstatic --noinput

# Create demo user
podman-compose exec backend python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@example.com', 'demo123')
EOF

# Seed database
podman-compose exec backend python seed_realistic_data.py
```

**Note**: Most `docker` and `docker compose` commands work with `podman` and `podman-compose` respectively.

### Option 3: LXC/LXD Containers

LXC/LXD provides system containers that are more lightweight than VMs.

#### Install LXD

**Ubuntu**:
```bash
sudo snap install lxd
sudo lxd init  # Follow the prompts
```

#### Create Container

```bash
# Launch Ubuntu container
lxc launch ubuntu:22.04 healthcare-app

# Enter container
lxc exec healthcare-app -- bash

# Inside container, follow Ubuntu/Debian native setup instructions
# ... (steps 1-10 from Option 1)

# Exit container
exit

# Access from host
lxc list  # Get container IP
# Access at http://<container-ip>:8000
```

### Option 4: Vagrant (Virtual Machine)

Vagrant provides reproducible development environments using VMs.

#### Install Vagrant

Download from: https://www.vagrantup.com/downloads

#### Create Vagrantfile

Create `Vagrantfile` in the project root:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"

  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5432, host: 5432

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    # Update system
    apt-get update

    # Install dependencies
    apt-get install -y python3.11 python3.11-venv python3-pip \
                       postgresql-16 redis-server rabbitmq-server \
                       nodejs npm git

    # Setup database
    sudo -u postgres psql -c "CREATE DATABASE healthcare_db;"
    sudo -u postgres psql -c "CREATE USER healthcare_user WITH PASSWORD 'vagrant123';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;"

    # Clone and setup project
    cd /vagrant
    cd backend
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic --noinput

    cd ../frontend
    npm install
    npm run build
  SHELL
end
```

#### Start Vagrant VM

```bash
# Start VM
vagrant up

# SSH into VM
vagrant ssh

# Run services
cd /vagrant/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

Access at: http://localhost:8000

### Option 5: containerd with nerdctl

containerd is a container runtime, and nerdctl is a Docker-compatible CLI.

#### Install containerd and nerdctl

**Ubuntu/Debian**:
```bash
# Install containerd
sudo apt install -y containerd

# Install nerdctl
wget https://github.com/containerd/nerdctl/releases/download/v1.7.0/nerdctl-1.7.0-linux-amd64.tar.gz
sudo tar Cxzvvf /usr/local/bin nerdctl-1.7.0-linux-amd64.tar.gz
```

#### Run with nerdctl

```bash
# Use nerdctl with docker-compose.yml (requires buildkit)
nerdctl compose up -d

# Or use nerdctl commands similar to docker
nerdctl build -t healthcare-backend ./backend
nerdctl run -d -p 8000:8000 healthcare-backend
```

### Troubleshooting Non-Docker Setups

#### PostgreSQL Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Test connection
psql -h localhost -U healthcare_user -d healthcare_db
```

#### Redis Connection Issues
```bash
# Check Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

#### RabbitMQ Connection Issues
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Check RabbitMQ logs
sudo tail -f /var/log/rabbitmq/rabbit@hostname.log

# List users
sudo rabbitmqctl list_users
```

#### Python Virtual Environment Issues
```bash
# Ensure you're in the virtual environment
which python  # Should show venv path

# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Port Conflicts
```bash
# Find process using a port
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process
sudo kill -9 <PID>
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R $USER:$USER /var/www/visma-healthcare

# Fix PostgreSQL permissions
sudo -u postgres psql healthcare_db -c "GRANT ALL ON SCHEMA public TO healthcare_user;"
```

### Option 6: Ansible Automation (Recommended for Production)

Ansible provides automated, repeatable, and production-ready deployment with infrastructure as code.

#### What is Ansible?

Ansible is an open-source automation tool that simplifies:
- **Infrastructure provisioning**: Automated server setup
- **Configuration management**: Consistent configuration across servers
- **Application deployment**: Repeatable deployments
- **Multi-server orchestration**: Deploy to multiple servers simultaneously

#### Why Use Ansible?

- **Idempotent**: Safe to run multiple times
- **Agentless**: No software to install on target servers
- **YAML-based**: Human-readable configuration
- **Production-ready**: Includes systemd services, Nginx, and proper logging
- **Scalable**: Deploy to multiple servers with one command
- **Reproducible**: Same results every time

#### Prerequisites

**On your local machine (control node):**
```bash
# Ubuntu/Debian
sudo apt install ansible

# macOS
brew install ansible

# Python pip
pip install ansible
```

**Target server requirements:**
- Ubuntu 20.04+ or Debian 11+
- SSH access with sudo privileges
- 4GB+ RAM (8GB recommended)
- 20GB+ free disk space

#### Quick Start (One Command!)

**Local Deployment:**
```bash
# Option 1: Using the deployment script
cd ansible
./deploy.sh

# Option 2: Using Makefile
make ansible-deploy
```

**Remote Deployment:**
```bash
# Option 1: Using the deployment script
cd ansible
./deploy.sh --remote 192.168.1.100

# Option 2: Using Makefile
make ansible-deploy-remote HOST=192.168.1.100
```

That's it! The script will:
- ✅ Auto-install Ansible if needed
- ✅ Generate secure secrets automatically
- ✅ Create all configuration files
- ✅ Deploy the complete application stack
- ✅ Set up systemd services
- ✅ Create demo user and seed database

**Access your application** (after 10-15 minutes):
- **Frontend**: http://localhost/ (or http://your-server-ip/)
- **Backend API**: http://localhost:8000/
- **API Docs**: http://localhost:8000/api/docs/
- **Demo login**: username `demo`, password `demo123`

#### Manual Configuration (Optional)

If you prefer manual configuration instead of the automated script:

1. **Install Ansible**:
   ```bash
   # Ubuntu/Debian
   sudo apt install ansible

   # macOS
   brew install ansible
   ```

2. **Configure servers** - Edit `ansible/inventory/hosts.ini`:
   ```ini
   [healthcare_servers]
   localhost ansible_connection=local
   ```

3. **Configure variables** - Edit `ansible/inventory/group_vars/all.yml`:
   ```yaml
   django_secret_key: "your-secure-random-string"
   db_password: "your-secure-password"
   rabbitmq_password: "your-secure-password"
   nginx_server_name: "localhost"
   ```

4. **Run playbook**:
   ```bash
   cd ansible
   ansible-playbook -i inventory/hosts.ini playbook.yml
   ```

#### What Gets Deployed

The Ansible playbook automatically:

1. **System Setup**:
   - Installs Python 3.11, Node.js 18, and system dependencies
   - Creates dedicated application user
   - Clones the repository

2. **Infrastructure**:
   - PostgreSQL 16 with configured database and user
   - Redis 7 for caching
   - RabbitMQ 3 for message queuing

3. **Application**:
   - Django backend with Gunicorn
   - Vue.js frontend with Nginx
   - Celery workers for async tasks

4. **Services**:
   - All components configured as systemd services
   - Auto-start on system boot
   - Proper logging to `/var/log/healthcare/`

5. **Initial Data** (optional):
   - Demo user creation
   - Database seeding with sample data

#### Deployment Options

**Deploy specific components:**
```bash
# Only infrastructure (database, cache, messaging)
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "setup"

# Only application (backend, frontend, workers)
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "app"

# Only backend
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "backend"

# Only frontend
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "frontend"
```

**Test before deploying:**
```bash
# Dry run (check what would change)
ansible-playbook -i inventory/hosts.ini playbook.yml --check

# Verbose output
ansible-playbook -i inventory/hosts.ini playbook.yml -v
```

**Advanced deployment options:**
```bash
# Deploy with custom SSH user
./deploy.sh --remote 192.168.1.100 --user admin

# Deploy with specific SSH key
./deploy.sh --remote 192.168.1.100 --key ~/.ssh/my-key.pem

# Interactive mode (asks questions)
./deploy.sh --interactive

# Show all options
./deploy.sh --help
```

**Update existing deployment:**
```bash
# Update application code only
make ansible-update

# Update backend only
make ansible-backend

# Update frontend only
make ansible-frontend

# Check what would change
make ansible-check
```

#### Managing Services

After deployment, manage services via systemd:

```bash
# Check status
sudo systemctl status healthcare-backend
sudo systemctl status healthcare-celery-worker
sudo systemctl status healthcare-celery-beat

# Restart services
sudo systemctl restart healthcare-backend
sudo systemctl restart healthcare-celery-worker

# View logs
sudo journalctl -u healthcare-backend -f
sudo journalctl -u healthcare-celery-worker -f

# View application logs
tail -f /var/log/healthcare/backend.log
tail -f /var/log/healthcare/celery-worker.log
```

#### Updating the Application

To update to the latest version:

```bash
# Re-run the playbook (only updates changed components)
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "app"
```

#### Security Best Practices

1. **Encrypt sensitive data** with Ansible Vault:
   ```bash
   ansible-vault encrypt inventory/group_vars/all.yml
   ansible-vault edit inventory/group_vars/all.yml
   ```

2. **Use strong passwords** in `all.yml`:
   - `django_secret_key`: Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
   - `db_password`: Use strong random password
   - `rabbitmq_password`: Use strong random password

3. **Configure firewall**:
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

4. **Enable SSL** with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

#### Multi-Server Deployment

Deploy to multiple servers simultaneously:

```ini
# inventory/hosts.ini
[healthcare_servers]
production-1 ansible_host=192.168.1.100 ansible_user=ubuntu
production-2 ansible_host=192.168.1.101 ansible_user=ubuntu
staging ansible_host=192.168.1.102 ansible_user=ubuntu
```

Run playbook on all servers:
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml
```

Or target specific servers:
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --limit production-1
```

#### Customization

Edit `inventory/group_vars/all.yml` to customize:

```yaml
# Performance tuning
gunicorn_workers: 4              # Gunicorn worker processes
celery_worker_concurrency: 4     # Celery worker processes
gunicorn_timeout: 120            # Request timeout

# Features
create_demo_user: true           # Create demo account
seed_database: true              # Add sample data
run_migrations: true             # Run database migrations

# Application
app_directory: /var/www/visma-healthcare
app_branch: main                 # Git branch to deploy
```

#### Troubleshooting

**Test connectivity:**
```bash
ansible -i inventory/hosts.ini healthcare_servers -m ping
```

**Check what would change:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --check --diff
```

**View detailed logs:**
```bash
# On the server
sudo journalctl -u healthcare-backend -n 100
tail -f /var/log/healthcare/backend.log
tail -f /var/log/nginx/healthcare-error.log
```

**Re-run failed tasks:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --start-at-task="Install Python dependencies"
```

#### Documentation

For detailed Ansible documentation, see: [ansible/README.md](ansible/README.md)

Includes:
- Complete variable reference
- Advanced deployment scenarios
- Service management
- Backup strategies
- Multi-environment setup
- CI/CD integration

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
