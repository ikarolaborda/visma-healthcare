# Vagrant VM Setup Guide

## Why Vagrant?

Vagrant provides a **completely isolated virtual machine** for running the Healthcare application. This means:

- ✅ **No conflicts** with your host system
- ✅ **No permission issues** with git or files
- ✅ **Clean environment** that can be easily destroyed and recreated
- ✅ **Production-like** setup matching actual deployment
- ✅ **Portable** across Windows, macOS, and Linux

## Prerequisites

### 1. Install VirtualBox

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install virtualbox virtualbox-ext-pack
```

**macOS:**
```bash
brew install --cask virtualbox
```

**Windows:**
Download from: https://www.virtualbox.org/wiki/Downloads

### 2. Install Vagrant

**Ubuntu/Debian:**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
sudo apt install vagrant
```

**macOS:**
```bash
brew install vagrant
```

**Windows:**
Download from: https://www.vagrantup.com/downloads

### 3. Verify Installation

```bash
vagrant --version
vboxmanage --version
```

## Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# Start VM and deploy application
make vagrant-up

# Access the application
# - Frontend: http://localhost:8080
# - Backend API: http://localhost:8080/api/
# - Admin: http://localhost:8080/admin/
# - Direct VM: http://192.168.56.10

# SSH into VM
make vagrant-ssh

# View logs
make vagrant-logs

# Stop VM
make vagrant-halt

# Restart and re-provision
make vagrant-reload

# Seed database with realistic data (if needed)
make vagrant-seed

# Create demo user (if needed)
make vagrant-create-demo-user

# Destroy VM completely
make vagrant-destroy
```

### Option 2: Using Helper Script

```bash
# Start VM
./vagrant-deploy.sh up

# Manage VM
./vagrant-deploy.sh ssh
./vagrant-deploy.sh logs
./vagrant-deploy.sh halt
./vagrant-deploy.sh destroy
```

### Option 3: Direct Vagrant Commands

```bash
# Start VM
vagrant up

# SSH into VM
vagrant ssh

# Stop VM
vagrant halt

# Restart VM
vagrant reload

# Destroy VM
vagrant destroy
```

## First Time Setup

The first time you run `make vagrant-up` or `vagrant up`:

1. **Downloads Ubuntu 24.04** (~1.5GB) - this is cached for future use
2. **Creates a VM** with 4GB RAM and 2 CPUs
3. **Installs all dependencies**:
   - Python 3.11
   - Node.js 22
   - PostgreSQL 16
   - Redis 7
   - RabbitMQ 3
   - Nginx
4. **Deploys the application**:
   - Creates virtual environment
   - Installs Python packages
   - Runs database migrations
   - Builds frontend
   - Configures services
5. **Starts all services**

**This takes 10-15 minutes the first time**. Subsequent starts are much faster (1-2 minutes).

## Accessing the Application

### From Host Machine

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8080/api/
- **Admin Panel**: http://localhost:8080/admin/
- **API Docs**: http://localhost:8080/api/docs/

### Direct VM Access

- **All services**: http://192.168.56.10

### Inside the VM

```bash
# SSH into VM
make vagrant-ssh

# Application directory
cd /opt/healthcare

# Check services
sudo systemctl status healthcare-backend
sudo systemctl status healthcare-celery-worker
sudo systemctl status healthcare-celery-beat

# View logs
sudo journalctl -u healthcare-backend -f
sudo tail -f /var/log/healthcare/celery-worker.log
```

## Port Mappings

| Service | VM Port | Host Port | URL |
|---------|---------|-----------|-----|
| Nginx (Frontend/Proxy) | 80 | 8080 | http://localhost:8080 |
| Gunicorn (Backend) | 8000 | 8000 | http://localhost:8000 |

## Troubleshooting

### Connection Refused

**Problem**: Getting "connection refused" when accessing http://localhost:8080

**Solutions**:

1. **Check if VM is running**:
   ```bash
   vagrant status
   # Should show "running"
   ```

2. **Check if services are running inside VM**:
   ```bash
   vagrant ssh -c "sudo systemctl status healthcare-backend"
   vagrant ssh -c "sudo systemctl status nginx"
   ```

3. **Check port forwarding**:
   ```bash
   vagrant port
   # Should show: 80 (guest) => 8080 (host)
   ```

4. **Try direct VM access**:
   ```bash
   curl http://192.168.56.10
   ```

5. **Re-provision if needed**:
   ```bash
   make vagrant-reload
   ```

### VM Won't Start

**Problem**: `vagrant up` fails

**Solutions**:

1. **Check VirtualBox is running**:
   ```bash
   vboxmanage list vms
   ```

2. **Destroy and recreate**:
   ```bash
   vagrant destroy -f
   vagrant up
   ```

3. **Check logs**:
   ```bash
   vagrant up --debug > vagrant.log 2>&1
   ```

### Services Not Starting

**Problem**: Services fail inside VM

**Solutions**:

1. **SSH into VM and check logs**:
   ```bash
   vagrant ssh
   sudo journalctl -u healthcare-backend -n 100
   sudo journalctl -u healthcare-celery-worker -n 100
   ```

2. **Re-run Ansible**:
   ```bash
   make vagrant-provision
   ```

3. **Check application directory**:
   ```bash
   vagrant ssh -c "ls -la /opt/healthcare"
   ```

## Making Changes

### Updating Application Code

When you make changes to your code:

1. **Option 1: Rsync changes to VM**
   ```bash
   vagrant rsync
   vagrant provision
   ```

2. **Option 2: Reload VM**
   ```bash
   make vagrant-reload
   ```

3. **Option 3: Manual inside VM**
   ```bash
   vagrant ssh
   cd /opt/healthcare
   # Make changes
   sudo systemctl restart healthcare-backend
   ```

### Updating Ansible Configuration

After changing Ansible playbooks or roles:

```bash
make vagrant-provision
```

## Resource Usage

The VM uses:
- **RAM**: 4GB (configurable in Vagrantfile)
- **CPU**: 2 cores (configurable in Vagrantfile)
- **Disk**: ~10GB (grows as needed)

To change resources, edit `Vagrantfile`:

```ruby
config.vm.provider "virtualbox" do |vb|
  vb.memory = "4096"  # Change this
  vb.cpus = 2         # Change this
end
```

Then reload:
```bash
vagrant reload
```

## Cleaning Up

### Stop VM (preserves state)
```bash
make vagrant-halt
```

### Destroy VM (deletes everything)
```bash
make vagrant-destroy
```

### Start fresh
```bash
make vagrant-destroy
make vagrant-up
```

## Common Commands Cheat Sheet

```bash
# Start VM
make vagrant-up

# Stop VM
make vagrant-halt

# Restart VM
make vagrant-reload

# Destroy VM
make vagrant-destroy

# SSH into VM
make vagrant-ssh

# View logs
make vagrant-logs

# Re-provision
make vagrant-provision

# Check status
make vagrant-status
```

## Next Steps

After the VM is running:

1. **Access the application** at http://localhost:8080
2. **Login with demo credentials**:
   - Username: `demo`
   - Password: `demo123`
3. **Explore the API docs** at http://localhost:8080/api/docs/
4. **SSH into the VM** to explore: `make vagrant-ssh`

## Support

For issues:
1. Check this guide's troubleshooting section
2. View VM logs: `vagrant ssh -c "sudo journalctl -xe"`
3. Check Ansible output during provisioning
4. Destroy and recreate if needed: `make vagrant-destroy && make vagrant-up`
