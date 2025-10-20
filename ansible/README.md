# Healthcare Patient Management System - Ansible Deployment

This directory contains Ansible playbooks and roles for automated deployment of the Healthcare Patient Management System.

## Overview

The Ansible playbook automates the complete deployment process including:

- System setup and dependencies
- PostgreSQL 16 database
- Redis 7 cache server
- RabbitMQ 3 message broker
- Django backend with Gunicorn
- Vue.js frontend with Nginx
- Celery workers for async tasks
- Systemd services for all components

## Prerequisites

### Control Node (Your Machine)

- **Ansible**: 2.10 or higher
- **Python**: 3.8 or higher
- **SSH access**: To target servers (for remote deployment)

Install Ansible:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# macOS
brew install ansible

# Python pip
pip install ansible
```

### Target Server(s)

- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: Minimum 20GB free space
- **User**: Sudo privileges
- **Python**: 3.8+ (usually pre-installed)

## Quick Start

### 1. Configure Inventory

Edit `inventory/hosts.ini` to specify your target server(s):

```ini
[healthcare_servers]
# For local deployment
localhost ansible_connection=local

# For remote deployment (uncomment and modify)
# production-server ansible_host=192.168.1.100 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### 2. Configure Variables

**IMPORTANT**: Edit `inventory/group_vars/all.yml` and change these values:

```yaml
# Security - CHANGE THESE!
django_secret_key: "your-secure-random-string-here"
db_password: "your-secure-database-password"
rabbitmq_password: "your-secure-rabbitmq-password"

# Application settings
app_directory: /var/www/visma-healthcare
nginx_server_name: your-domain.com  # Or IP address
```

For production, encrypt sensitive variables with ansible-vault:

```bash
ansible-vault encrypt inventory/group_vars/all.yml
```

### 3. Run the Playbook

**Local deployment:**
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbook.yml
```

**Remote deployment:**
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbook.yml --ask-become-pass
```

**With encrypted vault:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --ask-vault-pass --ask-become-pass
```

### 4. Access the Application

After successful deployment:

- **Frontend**: http://your-server-ip/
- **Backend API**: http://your-server-ip:8000/
- **API Docs**: http://your-server-ip:8000/api/docs/
- **Django Admin**: http://your-server-ip:8000/admin/
- **RabbitMQ Management**: http://your-server-ip:15672/ (guest/guest)

**Demo credentials:**
- Username: `demo`
- Password: `demo123`

## Deployment Options

### Partial Deployment with Tags

Run only specific parts of the deployment:

```bash
# Install only infrastructure (database, cache, messaging)
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "setup"

# Deploy only application code (backend, frontend, celery)
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "app"

# Deploy only backend
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "backend"

# Deploy only frontend
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "frontend"
```

Available tags:
- `common` - System setup
- `postgresql`, `database` - Database
- `redis`, `cache` - Cache server
- `rabbitmq`, `messaging` - Message broker
- `backend`, `django` - Backend application
- `frontend`, `vue`, `nginx` - Frontend application
- `celery`, `workers` - Celery workers
- `setup` - All infrastructure
- `app` - All application components

### Dry Run (Check Mode)

Test the playbook without making changes:

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --check
```

### Verbose Output

For detailed output during deployment:

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml -v   # verbose
ansible-playbook -i inventory/hosts.ini playbook.yml -vv  # more verbose
ansible-playbook -i inventory/hosts.ini playbook.yml -vvv # very verbose
```

## Configuration Variables

Edit `inventory/group_vars/all.yml` to customize your deployment:

### Application Settings
```yaml
app_name: healthcare
app_directory: /var/www/visma-healthcare
app_user: healthcare
app_repository: https://github.com/ikarolaborda/visma-healthcare.git
app_branch: main
```

### Django Settings
```yaml
django_debug: false  # Set to true for development
django_secret_key: "your-secret-key"
django_allowed_hosts: "localhost,127.0.0.1,your-domain.com"
```

### Database Settings
```yaml
db_name: healthcare_db
db_user: healthcare_user
db_password: "secure-password"
```

### Deployment Options
```yaml
create_demo_user: true      # Create demo user account
seed_database: true         # Seed with sample data
run_migrations: true        # Run database migrations
collect_static: true        # Collect Django static files
```

### Performance Tuning
```yaml
gunicorn_workers: 4         # Number of Gunicorn workers
gunicorn_timeout: 120       # Request timeout in seconds
celery_worker_concurrency: 4 # Celery worker processes
```

## Directory Structure

```
ansible/
├── playbook.yml              # Main playbook
├── inventory/
│   ├── hosts.ini            # Server inventory
│   └── group_vars/
│       └── all.yml          # Global variables
├── roles/
│   ├── common/              # System setup
│   │   └── tasks/
│   │       └── main.yml
│   ├── postgresql/          # Database
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── handlers/
│   │       └── main.yml
│   ├── redis/               # Cache
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── handlers/
│   │       └── main.yml
│   ├── rabbitmq/            # Message broker
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── handlers/
│   │       └── main.yml
│   ├── backend/             # Django application
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   └── templates/
│   │       ├── env.j2
│   │       └── healthcare-backend.service.j2
│   ├── frontend/            # Vue.js + Nginx
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   └── templates/
│   │       └── nginx-healthcare.conf.j2
│   └── celery/              # Celery workers
│       ├── tasks/
│       │   └── main.yml
│       ├── handlers/
│       │   └── main.yml
│       └── templates/
│           ├── healthcare-celery-worker.service.j2
│           └── healthcare-celery-beat.service.j2
└── README.md                # This file
```

## Managing Services

After deployment, services are managed via systemd:

```bash
# Check service status
sudo systemctl status healthcare-backend
sudo systemctl status healthcare-celery-worker
sudo systemctl status healthcare-celery-beat
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status rabbitmq-server

# Restart services
sudo systemctl restart healthcare-backend
sudo systemctl restart healthcare-celery-worker
sudo systemctl restart healthcare-celery-beat
sudo systemctl restart nginx

# View logs
sudo journalctl -u healthcare-backend -f
sudo journalctl -u healthcare-celery-worker -f
sudo journalctl -u healthcare-celery-beat -f

# Check all healthcare services
sudo systemctl list-units "healthcare-*"
```

## Updating the Application

To update the application to the latest version:

```bash
# Update code and restart services
ansible-playbook -i inventory/hosts.ini playbook.yml --tags "app"

# Or manually on the server
cd /var/www/visma-healthcare
sudo -u healthcare git pull
sudo -u healthcare /var/www/visma-healthcare/backend/venv/bin/pip install -r backend/requirements.txt
sudo -u healthcare /var/www/visma-healthcare/backend/venv/bin/python backend/manage.py migrate
sudo -u healthcare /var/www/visma-healthcare/backend/venv/bin/python backend/manage.py collectstatic --noinput
sudo systemctl restart healthcare-backend healthcare-celery-worker healthcare-celery-beat
```

## Security Best Practices

1. **Use Ansible Vault** for sensitive data:
   ```bash
   ansible-vault encrypt inventory/group_vars/all.yml
   ansible-vault edit inventory/group_vars/all.yml
   ```

2. **Change default passwords** in `all.yml`:
   - `django_secret_key`
   - `db_password`
   - `rabbitmq_password`

3. **Set up firewall** on your server:
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS (if using SSL)
   sudo ufw enable
   ```

4. **Enable SSL/TLS** for production:
   - Install certbot: `sudo apt install certbot python3-certbot-nginx`
   - Get certificate: `sudo certbot --nginx -d your-domain.com`

5. **Regular updates**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

## Troubleshooting

### Playbook Fails

**Check connectivity:**
```bash
ansible -i inventory/hosts.ini healthcare_servers -m ping
```

**Check Python version:**
```bash
ansible -i inventory/hosts.ini healthcare_servers -m command -a "python3 --version"
```

**Run with verbose output:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml -vvv
```

### Service Issues

**Check service logs:**
```bash
sudo journalctl -u healthcare-backend -n 100
sudo journalctl -u healthcare-celery-worker -n 100
```

**Check application logs:**
```bash
tail -f /var/log/healthcare/backend.log
tail -f /var/log/healthcare/celery-worker.log
tail -f /var/log/nginx/healthcare-error.log
```

**Test database connection:**
```bash
sudo -u postgres psql -d healthcare_db -c "\dt"
```

**Test Redis:**
```bash
redis-cli ping
```

**Test RabbitMQ:**
```bash
sudo rabbitmqctl status
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R healthcare:healthcare /var/www/visma-healthcare

# Fix Python virtual environment
sudo -u healthcare python3.11 -m venv /var/www/visma-healthcare/backend/venv
```

## Multi-Server Deployment

For deploying to multiple servers (e.g., separate database server):

1. **Edit inventory:**
   ```ini
   [database_servers]
   db-server ansible_host=192.168.1.100

   [app_servers]
   app-server-1 ansible_host=192.168.1.101
   app-server-2 ansible_host=192.168.1.102

   [healthcare_servers:children]
   database_servers
   app_servers
   ```

2. **Create host-specific variables:**
   ```bash
   mkdir -p inventory/host_vars
   echo "db_host: 192.168.1.100" > inventory/host_vars/app-server-1.yml
   ```

## Advanced Usage

### Custom Roles

Create custom roles for additional components:

```bash
mkdir -p roles/monitoring/tasks
```

Add to `playbook.yml`:
```yaml
roles:
  - monitoring
```

### Integration with CI/CD

Example GitLab CI configuration:

```yaml
deploy:
  stage: deploy
  script:
    - ansible-playbook -i inventory/hosts.ini playbook.yml --ask-vault-pass
  only:
    - main
```

## Support

For issues with Ansible deployment:

1. Check the troubleshooting section above
2. Review Ansible documentation: https://docs.ansible.com/
3. Open an issue on GitHub with playbook output

## License

This Ansible configuration is part of the Healthcare Patient Management System and follows the same MIT License.
