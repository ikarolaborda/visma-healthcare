#!/bin/bash
#
# Verify all Vagrant files exist after cloning
#

echo "Checking for Vagrant files..."
echo

files=(
    "Vagrantfile"
    "vagrant-deploy.sh"
    "install-vagrant.sh"
    "VAGRANT_SETUP.md"
    "ansible/inventory/vagrant.ini"
    "ansible/inventory/group_vars/vagrant.yml"
)

missing=0

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✓ $file"
    else
        echo "✗ MISSING: $file"
        missing=$((missing + 1))
    fi
done

echo
if [[ $missing -eq 0 ]]; then
    echo "✓ All Vagrant files present!"
    echo
    echo "Next steps:"
    echo "  1. Run: ./install-vagrant.sh"
    echo "  2. Then: make vagrant-up"
else
    echo "✗ $missing files missing!"
    echo
    echo "Try:"
    echo "  git pull origin main"
    echo "  git checkout main"
fi
