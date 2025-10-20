#!/bin/bash
#
# Healthcare Application Automated Deployment Script
# This script automates the complete deployment process using Ansible
#
# Usage:
#   ./deploy.sh                    # Deploy locally
#   ./deploy.sh remote <host>      # Deploy to remote host
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY_DIR="${SCRIPT_DIR}/inventory"
GROUP_VARS_FILE="${INVENTORY_DIR}/group_vars/all.yml"
HOSTS_FILE="${INVENTORY_DIR}/hosts.ini"
SECRETS_FILE="${INVENTORY_DIR}/.secrets.yml"
PLAYBOOK="${SCRIPT_DIR}/playbook.yml"

# Default values
DEPLOYMENT_MODE="${1:-local}"
REMOTE_HOST="${2:-}"
APP_DIRECTORY="/var/www/visma-healthcare"
APP_NAME="healthcare"
APP_USER="healthcare"
APP_GROUP="healthcare"

# Function to print colored messages
print_message() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

print_header() {
    echo
    print_message "${BLUE}" "=============================================="
    print_message "${BLUE}" "$@"
    print_message "${BLUE}" "=============================================="
    echo
}

print_success() {
    print_message "${GREEN}" "✓ $@"
}

print_error() {
    print_message "${RED}" "✗ $@"
}

print_warning() {
    print_message "${YELLOW}" "⚠ $@"
}

print_info() {
    print_message "${BLUE}" "ℹ $@"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check and install Ansible
check_ansible() {
    print_header "Checking Ansible Installation"
    
    if command_exists ansible-playbook; then
        ANSIBLE_VERSION=$(ansible --version | head -n1 | cut -d' ' -f2)
        print_success "Ansible is already installed (version: ${ANSIBLE_VERSION})"
        return 0
    fi
    
    print_warning "Ansible is not installed. Installing now..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            print_info "Detected Debian/Ubuntu system"
            sudo apt-get update
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository -y ppa:ansible/ansible
            sudo apt-get update
            sudo apt-get install -y ansible
        elif command_exists yum; then
            print_info "Detected RHEL/CentOS system"
            sudo yum install -y epel-release
            sudo yum install -y ansible
        elif command_exists dnf; then
            print_info "Detected Fedora system"
            sudo dnf install -y ansible
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "Detected macOS system"
        if command_exists brew; then
            brew install ansible
        else
            print_error "Homebrew is not installed. Please install it from https://brew.sh"
            exit 1
        fi
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    if command_exists ansible-playbook; then
        print_success "Ansible installed successfully"
    else
        print_error "Failed to install Ansible"
        exit 1
    fi
}

# Function to generate secrets
generate_secrets() {
    print_header "Generating Secrets"
    
    if [[ -f "${SECRETS_FILE}" ]]; then
        print_warning "Secrets file already exists at ${SECRETS_FILE}"
        read -p "Do you want to regenerate secrets? This will overwrite existing secrets (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Using existing secrets"
            return 0
        fi
    fi
    
    print_info "Generating secure random secrets..."
    
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python3 "${SCRIPT_DIR}/generate-secrets.py" "${SECRETS_FILE}"
    
    if [[ -f "${SECRETS_FILE}" ]]; then
        print_success "Secrets generated successfully"
        chmod 600 "${SECRETS_FILE}"
    else
        print_error "Failed to generate secrets"
        exit 1
    fi
}

# Function to create inventory
create_inventory() {
    print_header "Creating Ansible Inventory"
    
    mkdir -p "${INVENTORY_DIR}/group_vars"
    
    if [[ "${DEPLOYMENT_MODE}" == "local" ]]; then
        print_info "Creating local inventory..."
        cat > "${HOSTS_FILE}" << 'INVENTORY_EOF'
[healthcare_servers]
localhost ansible_connection=local

[healthcare_servers:vars]
ansible_python_interpreter=/usr/bin/python3
INVENTORY_EOF
    elif [[ "${DEPLOYMENT_MODE}" == "remote" ]]; then
        if [[ -z "${REMOTE_HOST}" ]]; then
            print_error "Remote host not specified"
            print_info "Usage: ./deploy.sh remote <hostname_or_ip>"
            exit 1
        fi
        
        print_info "Creating remote inventory for ${REMOTE_HOST}..."
        cat > "${HOSTS_FILE}" << INVENTORY_EOF
[healthcare_servers]
${REMOTE_HOST} ansible_user=ubuntu ansible_become=yes

[healthcare_servers:vars]
ansible_python_interpreter=/usr/bin/python3
INVENTORY_EOF
    else
        print_error "Invalid deployment mode: ${DEPLOYMENT_MODE}"
        print_info "Usage: ./deploy.sh [local|remote] [hostname]"
        exit 1
    fi
    
    print_success "Inventory created at ${HOSTS_FILE}"
}

# Function to create group variables
create_group_vars() {
    print_header "Creating Group Variables"
    
    # Load secrets
    if [[ ! -f "${SECRETS_FILE}" ]]; then
        print_error "Secrets file not found at ${SECRETS_FILE}"
        exit 1
    fi
    
    # Parse secrets from YAML
    DJANGO_SECRET_KEY=$(grep 'django_secret_key:' "${SECRETS_FILE}" | cut -d'"' -f2)
    DB_PASSWORD=$(grep 'db_password:' "${SECRETS_FILE}" | cut -d'"' -f2)
    RABBITMQ_PASSWORD=$(grep 'rabbitmq_password:' "${SECRETS_FILE}" | cut -d'"' -f2)
    
    print_info "Creating configuration file..."
    
    cat > "${GROUP_VARS_FILE}" << GROUP_VARS_EOF
---
# Application Configuration
app_name: ${APP_NAME}
app_directory: ${APP_DIRECTORY}
app_user: ${APP_USER}
app_group: ${APP_GROUP}
git_repo: https://github.com/yourusername/visma-healthcare.git
git_branch: main

# Python Configuration
python_version: "3.11"

# Node.js Configuration
nodejs_version: "22.x"

# PostgreSQL Configuration
db_name: ${APP_NAME}_db
db_user: ${APP_USER}
db_password: "${DB_PASSWORD}"
db_host: localhost
db_port: 5432
postgresql_version: "16"

# Redis Configuration
redis_host: localhost
redis_port: 6379
redis_db: 0
redis_url: "redis://localhost:6379/0"

# RabbitMQ Configuration
rabbitmq_user: ${APP_USER}
rabbitmq_password: "${RABBITMQ_PASSWORD}"
rabbitmq_vhost: "/${APP_NAME}"
celery_broker_url: "amqp://{{ rabbitmq_user }}:{{ rabbitmq_password }}@localhost:5672/{{ rabbitmq_vhost }}"

# Django Configuration
django_secret_key: "${DJANGO_SECRET_KEY}"
django_debug: false
django_allowed_hosts: "localhost,127.0.0.1"
cors_allowed_origins: "http://localhost,http://127.0.0.1"

# Gunicorn Configuration
gunicorn_workers: 4
gunicorn_bind: "127.0.0.1:8000"
gunicorn_timeout: 120

# Celery Configuration
celery_worker_concurrency: 4
celery_worker_log_level: info
celery_result_backend: "redis://localhost:6379/1"

# Nginx Configuration
nginx_port: 80
nginx_server_name: localhost

# Deployment Settings
deploy_env: production
run_migrations: true
collect_static: true
GROUP_VARS_EOF
    
    print_success "Group variables created at ${GROUP_VARS_FILE}"
}

# Function to display deployment info
display_deployment_info() {
    print_header "Deployment Configuration"
    
    echo "Mode:            ${DEPLOYMENT_MODE}"
    if [[ "${DEPLOYMENT_MODE}" == "remote" ]]; then
        echo "Remote Host:     ${REMOTE_HOST}"
    fi
    echo "App Directory:   ${APP_DIRECTORY}"
    echo "App User:        ${APP_USER}"
    echo "App Name:        ${APP_NAME}"
    echo
}

# Function to run Ansible playbook
run_playbook() {
    print_header "Running Ansible Playbook"
    
    local ANSIBLE_OPTS=""
    
    if [[ "${DEPLOYMENT_MODE}" == "local" ]]; then
        ANSIBLE_OPTS="-K"  # Ask for sudo password
    fi
    
    print_info "Executing playbook..."
    print_warning "This may take several minutes depending on your internet connection and system resources"
    echo
    
    ansible-playbook \
        -i "${HOSTS_FILE}" \
        ${ANSIBLE_OPTS} \
        "${PLAYBOOK}" \
        -e "@${SECRETS_FILE}"
    
    local EXIT_CODE=$?
    
    if [[ ${EXIT_CODE} -eq 0 ]]; then
        print_success "Playbook execution completed successfully"
        return 0
    else
        print_error "Playbook execution failed with exit code ${EXIT_CODE}"
        return ${EXIT_CODE}
    fi
}

# Function to display post-deployment info
display_post_deployment_info() {
    print_header "Deployment Complete!"
    
    echo
    print_success "Healthcare application has been deployed successfully!"
    echo
    
    print_info "Access Information:"
    echo "  Frontend:      http://localhost"
    echo "  Backend API:   http://localhost/api/"
    echo "  FHIR API:      http://localhost/fhir/"
    echo "  Admin Panel:   http://localhost/admin/"
    echo
    
    print_info "Service Management:"
    echo "  Backend:       sudo systemctl status healthcare-backend"
    echo "  Celery Worker: sudo systemctl status healthcare-celery-worker"
    echo "  Celery Beat:   sudo systemctl status healthcare-celery-beat"
    echo "  Nginx:         sudo systemctl status nginx"
    echo "  PostgreSQL:    sudo systemctl status postgresql"
    echo "  Redis:         sudo systemctl status redis"
    echo "  RabbitMQ:      sudo systemctl status rabbitmq-server"
    echo
    
    print_info "Application Logs:"
    echo "  Backend:       tail -f /var/log/${APP_NAME}/gunicorn.log"
    echo "  Celery Worker: tail -f /var/log/${APP_NAME}/celery-worker.log"
    echo "  Celery Beat:   tail -f /var/log/${APP_NAME}/celery-beat.log"
    echo "  Nginx Access:  tail -f /var/log/nginx/healthcare-access.log"
    echo "  Nginx Error:   tail -f /var/log/nginx/healthcare-error.log"
    echo
    
    print_warning "Important Files:"
    echo "  Secrets:       ${SECRETS_FILE}"
    echo "  Inventory:     ${HOSTS_FILE}"
    echo "  Config:        ${GROUP_VARS_FILE}"
    echo
    
    print_warning "Please keep the secrets file (${SECRETS_FILE}) secure!"
    echo
    
    print_info "To update the deployment:"
    echo "  make ansible-update"
    echo
    
    print_info "To check deployment status without changes:"
    echo "  make ansible-check"
    echo
}

# Function to verify prerequisites
verify_prerequisites() {
    print_header "Verifying Prerequisites"
    
    local MISSING_DEPS=()
    
    if ! command_exists python3; then
        MISSING_DEPS+=("python3")
    fi
    
    if ! command_exists git; then
        MISSING_DEPS+=("git")
    fi
    
    if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${MISSING_DEPS[*]}"
        print_info "Please install them before continuing"
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Function to show usage
show_usage() {
    cat << USAGE_EOF
Healthcare Application Deployment Script

Usage:
  ./deploy.sh [MODE] [OPTIONS]

Modes:
  local              Deploy locally on this machine (default)
  remote <host>      Deploy to remote host

Examples:
  ./deploy.sh                          # Deploy locally
  ./deploy.sh local                    # Deploy locally (explicit)
  ./deploy.sh remote 192.168.1.100    # Deploy to remote host
  ./deploy.sh remote server.example.com

Notes:
  - For local deployment, you will be prompted for sudo password
  - For remote deployment, SSH key authentication should be configured
  - Secrets are generated automatically on first run
  - Configuration can be customized in ${GROUP_VARS_FILE}

USAGE_EOF
}

# Main execution
main() {
    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    print_header "Healthcare Application Automated Deployment"
    
    # Verify prerequisites
    verify_prerequisites
    
    # Check and install Ansible
    check_ansible
    
    # Generate secrets
    generate_secrets
    
    # Create inventory
    create_inventory
    
    # Create group variables
    create_group_vars
    
    # Display deployment info
    display_deployment_info
    
    # Confirm before proceeding
    if [[ ! "${CI:-false}" == "true" ]]; then
        echo
        read -p "Proceed with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Deployment cancelled by user"
            exit 0
        fi
    fi
    
    # Run playbook
    if run_playbook; then
        display_post_deployment_info
        exit 0
    else
        print_error "Deployment failed. Please check the output above for errors."
        exit 1
    fi
}

# Run main function
main "$@"
