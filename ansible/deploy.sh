#!/bin/bash
set -e

################################################################################
# Healthcare Patient Management System - One-Command Deployment
# This script automates the complete deployment with zero manual configuration
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEPLOYMENT_TYPE="local"
REMOTE_HOST=""
REMOTE_USER="ubuntu"
SSH_KEY=""
INTERACTIVE=false
APP_DIR="/var/www/visma-healthcare"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "$1"
    echo "=============================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

################################################################################
# Parse Arguments
################################################################################

show_usage() {
    cat << EOF
Healthcare Patient Management System - Automated Deployment

Usage: $0 [OPTIONS]

Options:
    --local             Deploy to localhost (default)
    --remote HOST       Deploy to remote server
    --user USER         SSH user for remote deployment (default: ubuntu)
    --key PATH          SSH private key path
    --interactive       Interactive mode with prompts
    --help              Show this help message

Examples:
    # Deploy locally (simplest)
    $0

    # Deploy to remote server
    $0 --remote 192.168.1.100

    # Deploy to remote server with custom user and key
    $0 --remote 192.168.1.100 --user admin --key ~/.ssh/mykey

    # Interactive mode
    $0 --interactive

EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            DEPLOYMENT_TYPE="local"
            shift
            ;;
        --remote)
            DEPLOYMENT_TYPE="remote"
            REMOTE_HOST="$2"
            shift 2
            ;;
        --user)
            REMOTE_USER="$2"
            shift 2
            ;;
        --key)
            SSH_KEY="$2"
            shift 2
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            ;;
    esac
done

################################################################################
# Main Deployment
################################################################################

print_header "Healthcare Patient Management System - Automated Deployment"

# Change to ansible directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "Deployment directory: $SCRIPT_DIR"

################################################################################
# Step 1: Check/Install Prerequisites
################################################################################

print_header "Step 1: Checking Prerequisites"

# Check for Ansible
if ! command -v ansible &> /dev/null; then
    print_warning "Ansible not found. Installing..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ansible
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y ansible
        elif command -v yum &> /dev/null; then
            sudo yum install -y ansible
        else
            print_error "Could not install Ansible. Please install manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ansible
        else
            print_error "Homebrew not found. Please install Ansible manually."
            exit 1
        fi
    else
        print_error "Unsupported OS. Please install Ansible manually."
        exit 1
    fi

    print_success "Ansible installed"
else
    ANSIBLE_VERSION=$(ansible --version | head -n1)
    print_success "Ansible found: $ANSIBLE_VERSION"
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found"
    exit 1
fi
print_success "Python 3 found"

################################################################################
# Step 2: Generate Secrets
################################################################################

print_header "Step 2: Generating Secure Secrets"

# Make generate-secrets.py executable
chmod +x generate-secrets.py

# Generate secrets
DJANGO_SECRET=$(python3 generate-secrets.py --django-secret)
DB_PASSWORD=$(python3 generate-secrets.py --password)
RABBITMQ_PASSWORD=$(python3 generate-secrets.py --password)

print_success "Django secret key generated (50 characters)"
print_success "Database password generated (32 characters)"
print_success "RabbitMQ password generated (32 characters)"

################################################################################
# Step 3: Detect/Configure Deployment Target
################################################################################

print_header "Step 3: Configuring Deployment Target"

if [ "$DEPLOYMENT_TYPE" == "remote" ] && [ -z "$REMOTE_HOST" ] && [ "$INTERACTIVE" == true ]; then
    read -p "Enter remote server IP or hostname: " REMOTE_HOST
fi

if [ "$DEPLOYMENT_TYPE" == "local" ]; then
    print_info "Deployment type: LOCAL"
    TARGET_HOST="localhost"
    NGINX_SERVER_NAME="localhost"

    # Create inventory for local deployment
    cat > inventory/hosts.ini << EOF
# Healthcare Patient Management System - Inventory (Auto-generated)
[healthcare_servers]
localhost ansible_connection=local

[healthcare_servers:vars]
ansible_python_interpreter=/usr/bin/python3
deployment_env=development
EOF

else
    print_info "Deployment type: REMOTE"
    print_info "Target server: $REMOTE_HOST"
    print_info "SSH user: $REMOTE_USER"

    TARGET_HOST="$REMOTE_HOST"
    NGINX_SERVER_NAME="$REMOTE_HOST"

    # Build SSH options
    SSH_OPTIONS=""
    if [ -n "$SSH_KEY" ]; then
        SSH_OPTIONS="ansible_ssh_private_key_file=$SSH_KEY"
        print_info "SSH key: $SSH_KEY"
    fi

    # Create inventory for remote deployment
    cat > inventory/hosts.ini << EOF
# Healthcare Patient Management System - Inventory (Auto-generated)
[healthcare_servers]
production ansible_host=$REMOTE_HOST ansible_user=$REMOTE_USER $SSH_OPTIONS

[healthcare_servers:vars]
ansible_python_interpreter=/usr/bin/python3
deployment_env=production
EOF
fi

print_success "Inventory file created"

################################################################################
# Step 4: Create Configuration
################################################################################

print_header "Step 4: Creating Configuration"

# Create group_vars directory if it doesn't exist
mkdir -p inventory/group_vars

# Create configuration file
cat > inventory/group_vars/all.yml << EOF
---
# Healthcare Patient Management System - Configuration (Auto-generated)
# Generated on: $(date)

# Application Settings
app_name: healthcare
app_directory: $APP_DIR
app_user: healthcare
app_group: healthcare
app_repository: https://github.com/ikarolaborda/visma-healthcare.git
app_branch: main

# Python Settings
python_version: "3.11"

# Node.js Settings
nodejs_version: "18.x"

# Django Settings
django_debug: $( [ "$DEPLOYMENT_TYPE" == "local" ] && echo "true" || echo "false" )
django_secret_key: "$DJANGO_SECRET"
django_allowed_hosts: "localhost,127.0.0.1,$TARGET_HOST"

# Database Settings
db_name: healthcare_db
db_user: healthcare_user
db_password: "$DB_PASSWORD"
db_host: localhost
db_port: 5432

# Redis Settings
redis_host: localhost
redis_port: 6379
redis_url: "redis://localhost:6379/0"

# RabbitMQ Settings
rabbitmq_user: healthcare_user
rabbitmq_password: "$RABBITMQ_PASSWORD"
rabbitmq_vhost: /
celery_broker_url: "amqp://healthcare_user:$RABBITMQ_PASSWORD@localhost:5672//"
celery_result_backend: "redis://localhost:6379/1"

# CORS Settings
cors_allowed_origins: "http://localhost,http://$TARGET_HOST"

# Nginx Settings
nginx_server_name: "$NGINX_SERVER_NAME"
nginx_port: 80

# Gunicorn Settings
gunicorn_workers: 4
gunicorn_timeout: 120
gunicorn_bind: "0.0.0.0:8000"

# Celery Settings
celery_worker_concurrency: 4
celery_worker_log_level: info

# Deployment Options
create_demo_user: true
seed_database: true
run_migrations: true
collect_static: true

# Firewall Settings
configure_firewall: false
allowed_ports:
  - 80
  - 443
  - 8000

# Backup Settings
enable_database_backups: false
backup_directory: "$APP_DIR/backups"
backup_retention_days: 7
EOF

print_success "Configuration file created"

# Save secrets to a file for user reference
cat > .deployment-secrets.txt << EOF
Healthcare Patient Management System - Deployment Secrets
Generated on: $(date)

IMPORTANT: Keep this file secure and do not commit to version control!

Django Secret Key: $DJANGO_SECRET
Database Password: $DB_PASSWORD
RabbitMQ Password: $RABBITMQ_PASSWORD

Demo User Credentials:
Username: demo
Password: demo123
EOF

chmod 600 .deployment-secrets.txt
print_success "Secrets saved to .deployment-secrets.txt"

################################################################################
# Step 5: Run Ansible Playbook
################################################################################

print_header "Step 5: Running Ansible Playbook"

print_info "This may take 10-15 minutes depending on your system..."
echo ""

# Build ansible-playbook command
ANSIBLE_CMD="ansible-playbook -i inventory/hosts.ini playbook.yml"

if [ "$DEPLOYMENT_TYPE" == "remote" ]; then
    ANSIBLE_CMD="$ANSIBLE_CMD --ask-become-pass"
fi

# Run the playbook
if $ANSIBLE_CMD; then
    print_success "Ansible playbook completed successfully"
else
    print_error "Ansible playbook failed"
    print_info "Check the output above for errors"
    print_info "You can re-run this script to retry"
    exit 1
fi

################################################################################
# Step 6: Display Access Information
################################################################################

print_header "🎉 Deployment Complete!"

echo ""
print_success "Healthcare Patient Management System is now running!"
echo ""

if [ "$DEPLOYMENT_TYPE" == "local" ]; then
    cat << EOF
${GREEN}Access URLs:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Frontend:           http://localhost/
  Backend API:        http://localhost:8000/
  API Documentation:  http://localhost:8000/api/docs/
  Django Admin:       http://localhost:8000/admin/
  RabbitMQ Mgmt:      http://localhost:15672/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${YELLOW}Demo Credentials:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Username: demo
  Password: demo123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
else
    cat << EOF
${GREEN}Access URLs:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Frontend:           http://$REMOTE_HOST/
  Backend API:        http://$REMOTE_HOST:8000/
  API Documentation:  http://$REMOTE_HOST:8000/api/docs/
  Django Admin:       http://$REMOTE_HOST:8000/admin/
  RabbitMQ Mgmt:      http://$REMOTE_HOST:15672/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${YELLOW}Demo Credentials:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Username: demo
  Password: demo123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi

echo ""
print_info "Deployment secrets saved in: .deployment-secrets.txt"
print_warning "Keep .deployment-secrets.txt secure!"
echo ""

cat << EOF
${BLUE}Service Management:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Check status:    sudo systemctl status healthcare-backend
  Restart backend: sudo systemctl restart healthcare-backend
  View logs:       sudo journalctl -u healthcare-backend -f
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${BLUE}Next Steps:${NC}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Open http://$( [ "$DEPLOYMENT_TYPE" == "local" ] && echo "localhost" || echo "$REMOTE_HOST" )/ in your browser
  2. Login with demo credentials
  3. Explore the application!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

print_success "Deployment completed successfully! 🚀"
echo ""
