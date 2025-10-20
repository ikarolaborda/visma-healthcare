#!/bin/bash
#
# Vagrant VM Deployment Helper Script
# Simplifies common Vagrant operations for Healthcare Application
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Vagrant is installed
check_vagrant() {
    if ! command -v vagrant >/dev/null 2>&1; then
        print_error "Vagrant is not installed"
        print_info "Install Vagrant from: https://www.vagrantup.com/downloads"
        exit 1
    fi

    if ! command -v vboxmanage >/dev/null 2>&1; then
        print_error "VirtualBox is not installed"
        print_info "Install VirtualBox from: https://www.virtualbox.org/wiki/Downloads"
        exit 1
    fi

    print_success "Vagrant and VirtualBox are installed"
}

# Generate secrets if they don't exist
ensure_secrets() {
    if [[ ! -f "ansible/inventory/.secrets.yml" ]]; then
        print_info "Generating secrets..."
        python3 ansible/generate-secrets.py ansible/inventory/.secrets.yml
        print_success "Secrets generated"
    else
        print_info "Using existing secrets"
    fi
}

# Main commands
cmd_up() {
    print_header "Starting Healthcare VM"
    check_vagrant
    ensure_secrets
    vagrant up
    print_success "VM is up and running!"
    echo
    print_info "Access the application at:"
    echo "  - http://localhost:8080"
    echo "  - http://192.168.56.10"
    echo
    print_info "SSH into the VM:"
    echo "  vagrant ssh"
}

cmd_halt() {
    print_header "Stopping Healthcare VM"
    vagrant halt
    print_success "VM stopped"
}

cmd_destroy() {
    print_header "Destroying Healthcare VM"
    print_warning "This will delete the VM and all its data"
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY == "yes" ]]; then
        vagrant destroy -f
        print_success "VM destroyed"
    else
        print_info "Cancelled"
    fi
}

cmd_reload() {
    print_header "Reloading Healthcare VM"
    vagrant reload --provision
    print_success "VM reloaded"
}

cmd_provision() {
    print_header "Re-provisioning Healthcare VM"
    vagrant provision
    print_success "Provisioning complete"
}

cmd_ssh() {
    vagrant ssh
}

cmd_status() {
    print_header "Healthcare VM Status"
    vagrant status
}

cmd_logs() {
    print_header "Viewing Healthcare Logs"
    vagrant ssh -c "sudo journalctl -u healthcare-backend -f"
}

show_usage() {
    cat << EOF
Healthcare Application - Vagrant Deployment Helper

Usage:
  ./vagrant-deploy.sh [COMMAND]

Commands:
  up          Start the VM and deploy the application
  halt        Stop the VM
  destroy     Delete the VM completely
  reload      Restart the VM and re-provision
  provision   Re-run Ansible provisioning without restart
  ssh         SSH into the VM
  status      Show VM status
  logs        View application logs
  help        Show this help message

Examples:
  ./vagrant-deploy.sh up        # Start and deploy
  ./vagrant-deploy.sh ssh       # SSH into VM
  ./vagrant-deploy.sh halt      # Stop VM
  ./vagrant-deploy.sh destroy   # Delete VM

Notes:
  - Requires Vagrant and VirtualBox to be installed
  - First run will take several minutes to download Ubuntu and provision
  - Subsequent runs will be much faster

EOF
}

# Main execution
main() {
    COMMAND="${1:-help}"

    case "$COMMAND" in
        up)
            cmd_up
            ;;
        halt)
            cmd_halt
            ;;
        destroy)
            cmd_destroy
            ;;
        reload)
            cmd_reload
            ;;
        provision)
            cmd_provision
            ;;
        ssh)
            cmd_ssh
            ;;
        status)
            cmd_status
            ;;
        logs)
            cmd_logs
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
