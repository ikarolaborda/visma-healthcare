# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Use Ubuntu 24.04 LTS
  config.vm.box = "ubuntu/noble64"
  config.vm.hostname = "healthcare-vm"

  # Network configuration
  # Forward ports for accessing the application from host
  config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"

  # Private network for direct VM access
  config.vm.network "private_network", ip: "192.168.56.10"

  # VM resources
  config.vm.provider "virtualbox" do |vb|
    vb.name = "healthcare-app"
    vb.memory = "4096"
    vb.cpus = 2
  end

  # Sync the application directory to VM
  # Using rsync for better performance (one-way sync from host to VM)
  config.vm.synced_folder ".", "/vagrant",
    type: "rsync",
    rsync__exclude: [
      ".git/",
      "node_modules/",
      "backend/venv/",
      "backend/__pycache__/",
      "frontend/dist/",
      "frontend/node_modules/",
      ".env",
      "*.pyc",
      "*.log",
      ".npm/",
      ".cache/"
    ]

  # Install Ansible in the VM
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y software-properties-common
    add-apt-repository -y ppa:ansible/ansible
    apt-get update
    apt-get install -y ansible
  SHELL

  # Provision with Ansible (runs inside the VM)
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "/vagrant/ansible/playbook.yml"
    ansible.inventory_path = "/vagrant/ansible/inventory/vagrant.ini"
    ansible.limit = "all"
    ansible.verbose = false
    ansible.install = false  # Already installed above
    ansible.extra_vars = "/vagrant/ansible/inventory/.secrets.yml"
  end

  # Post-provision message
  config.vm.post_up_message = <<-MSG
    ========================================
    Healthcare Application VM is ready!
    ========================================

    Access the application:
    - Frontend:    http://localhost:8080
    - Backend API: http://localhost:8080/api/
    - Admin:       http://localhost:8080/admin/
    - Direct VM:   http://192.168.56.10

    SSH into VM:
    $ vagrant ssh

    Service management (inside VM):
    $ sudo systemctl status healthcare-backend
    $ sudo systemctl status healthcare-celery-worker
    $ sudo systemctl status healthcare-celery-beat

    View logs:
    $ sudo journalctl -u healthcare-backend -f
    $ sudo tail -f /var/log/healthcare/celery-worker.log

    Useful commands:
    $ vagrant halt       # Stop the VM
    $ vagrant up         # Start the VM
    $ vagrant reload     # Restart the VM
    $ vagrant destroy    # Delete the VM
    $ vagrant provision  # Re-run Ansible provisioning
    ========================================
  MSG
end
