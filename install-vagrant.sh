#!/bin/bash
#
# Install Vagrant and VirtualBox
# Supports Ubuntu/Debian, macOS, and provides instructions for Windows
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() { echo -e "${RED}✗ $@${NC}"; }
print_success() { echo -e "${GREEN}✓ $@${NC}"; }
print_info() { echo -e "${BLUE}ℹ $@${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $@${NC}"; }

print_header() {
    echo
    echo -e "${BLUE}=============================================="
    echo -e "$@"
    echo -e "==============================================$ {NC}"
    echo
}

check_installed() {
    if command -v vagrant >/dev/null 2>&1 && command -v vboxmanage >/dev/null 2>&1; then
        print_success "Vagrant and VirtualBox are already installed!"
        vagrant --version
        vboxmanage --version
        echo
        print_info "You can now run: make vagrant-up"
        exit 0
    fi
}

install_ubuntu() {
    print_header "Installing Vagrant and VirtualBox on Ubuntu/Debian"

    # Install VirtualBox
    print_info "Installing VirtualBox..."
    sudo apt update
    sudo apt install -y virtualbox virtualbox-ext-pack

    # Install Vagrant
    print_info "Installing Vagrant..."
    wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update
    sudo apt install -y vagrant

    print_success "Installation complete!"
    vagrant --version
    vboxmanage --version
}

install_macos() {
    print_header "Installing Vagrant and VirtualBox on macOS"

    if ! command -v brew >/dev/null 2>&1; then
        print_error "Homebrew is not installed"
        print_info "Install Homebrew from: https://brew.sh"
        print_info "Then run this script again"
        exit 1
    fi

    print_info "Installing VirtualBox..."
    brew install --cask virtualbox

    print_info "Installing Vagrant..."
    brew install vagrant

    print_success "Installation complete!"
    vagrant --version
    vboxmanage --version
}

install_windows() {
    print_header "Windows Installation Instructions"

    echo "Please install manually:"
    echo
    echo "1. VirtualBox:"
    echo "   https://www.virtualbox.org/wiki/Downloads"
    echo "   Download and run the Windows installer"
    echo
    echo "2. Vagrant:"
    echo "   https://www.vagrantup.com/downloads"
    echo "   Download and run the Windows installer"
    echo
    echo "3. Restart your terminal after installation"
    echo
    echo "4. Run: make vagrant-up"
}

main() {
    print_header "Healthcare Application - Vagrant Installer"

    check_installed

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/debian_version ]]; then
            install_ubuntu
        else
            print_error "Unsupported Linux distribution"
            print_info "Please install Vagrant and VirtualBox manually"
            print_info "Vagrant: https://www.vagrantup.com/downloads"
            print_info "VirtualBox: https://www.virtualbox.org/wiki/Downloads"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        install_macos
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        install_windows
        exit 0
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    echo
    print_success "Setup complete!"
    echo
    print_info "Next steps:"
    echo "  1. Run: make vagrant-up"
    echo "  2. Wait 10-15 minutes for first-time setup"
    echo "  3. Access: http://localhost:8080"
    echo
}

main "$@"
