# User Guide

## Getting Started

### Installation

#### From Source
```bash
# Clone the repository
git clone https://github.com/your-org/debian_transactional_installer.git
cd debian_transactional_installer

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package
pip install -e .
```

#### Using Docker
```bash
# Build the Docker image
docker build -t transactional-installer .

# Run the installer
docker run --privileged -v /var/lib/transactional-installer:/var/lib/transactional-installer transactional-installer --help
```

### Basic Usage

#### 1. Create a Package Template

Start by creating a template for your package:

```bash
transactional-installer create-template my-webapp 1.0.0 -o my-webapp.yml
```

This creates a basic template file that you can customize.

#### 2. Customize the Package

Edit the generated `my-webapp.yml` file:

```yaml
package:
  name: "my-webapp"
  version: "1.0.0"
  description: "A simple web application"
  author: "Your Name"
  license: "MIT"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx", "python3", "python3-pip"]
    rollback: "remove_packages"

  - type: "file_copy"
    src: "./app.conf"
    dest: "/etc/nginx/sites-available/my-webapp.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  - type: "systemd_service"
    service: "nginx"
    action: "enable"
    rollback: "disable"

  - type: "user_management"
    username: "webapp"
    action: "create"
    user_data:
      home: "/var/www/my-webapp"
      shell: "/bin/bash"
      groups: ["www-data"]
    rollback: "remove_user"

dependencies:
  - "debian-11"

requirements:
  min_memory: 512
  min_disk_space: 1000
  os_version: "11.0"
```

#### 3. Validate the Package

Before installing, validate your package:

```bash
transactional-installer validate my-webapp.yml
```

#### 4. Install the Package

Install the package (use `--dry-run` first to test):

```bash
# Test installation without making changes
sudo transactional-installer install my-webapp.yml --dry-run

# Perform actual installation
sudo transactional-installer install my-webapp.yml
```

#### 5. Monitor Installation

Check the status of your installation:

```bash
# List recent transactions
transactional-installer list

# Get detailed status of a specific transaction
transactional-installer status <transaction_id>
```

## Advanced Usage

### Complex Installation Scenarios

#### Web Application with Database

```yaml
package:
  name: "full-stack-app"
  version: "2.0.0"
  description: "Full-stack web application with database"

install_steps:
  # Install system packages
  - type: "apt_package"
    action: "install"
    packages: ["nginx", "postgresql", "python3", "python3-pip"]
    rollback: "remove_packages"

  # Create application user
  - type: "user_management"
    username: "appuser"
    action: "create"
    user_data:
      home: "/home/appuser"
      shell: "/bin/bash"
      groups: ["www-data", "postgres"]
    rollback: "remove_user"

  # Copy application files
  - type: "file_copy"
    src: "./app/"
    dest: "/var/www/full-stack-app/"
    owner: "appuser"
    group: "www-data"
    mode: "755"
    rollback: "restore_original"

  # Copy nginx configuration
  - type: "file_copy"
    src: "./nginx.conf"
    dest: "/etc/nginx/sites-available/full-stack-app.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  # Enable nginx site
  - type: "custom_script"
    script: "enable_nginx_site.sh"
    rollback_script: "disable_nginx_site.sh"

  # Setup database
  - type: "ansible_playbook"
    playbook: "setup_database.yml"
    rollback_playbook: "cleanup_database.yml"
    vars:
      db_name: "fullstackapp"
      db_user: "appuser"

  # Start services
  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "postgresql"
    action: "restart"
    rollback: "stop"

pre_install:
  - type: "script"
    script: "check_system_requirements.sh"

post_install:
  - type: "script"
    script: "post_install_setup.sh"

dependencies:
  - "debian-11"

requirements:
  min_memory: 2048
  min_disk_space: 5000
  os_version: "11.0"
```

#### Microservices Application

```yaml
package:
  name: "microservices-platform"
  version: "1.0.0"
  description: "Microservices platform with multiple services"

install_steps:
  # Install base dependencies
  - type: "apt_package"
    action: "install"
    packages: ["docker.io", "docker-compose", "nginx", "redis-server"]
    rollback: "remove_packages"

  # Create service users
  - type: "user_management"
    username: "api-service"
    action: "create"
    user_data:
      home: "/home/api-service"
      shell: "/bin/false"
      groups: ["docker"]
      system: true
    rollback: "remove_user"

  - type: "user_management"
    username: "web-service"
    action: "create"
    user_data:
      home: "/home/web-service"
      shell: "/bin/false"
      groups: ["docker"]
      system: true
    rollback: "remove_user"

  # Copy service configurations
  - type: "file_copy"
    src: "./services/"
    dest: "/opt/microservices/"
    owner: "root"
    group: "root"
    mode: "755"
    rollback: "restore_original"

  # Setup Docker networks
  - type: "custom_script"
    script: "setup_docker_networks.sh"
    rollback_script: "cleanup_docker_networks.sh"

  # Deploy services using Ansible
  - type: "ansible_playbook"
    playbook: "deploy_services.yml"
    rollback_playbook: "undeploy_services.yml"
    vars:
      environment: "production"
      service_count: 3

  # Configure nginx as reverse proxy
  - type: "file_copy"
    src: "./nginx/microservices.conf"
    dest: "/etc/nginx/sites-available/microservices.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  # Enable and start services
  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "redis"
    action: "restart"
    rollback: "stop"

requirements:
  min_memory: 4096
  min_disk_space: 10000
  os_version: "11.0"
```

### Rollback Strategies

#### Automatic Rollback

For simple operations, use automatic rollback:

```yaml
install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx"]
    rollback: "auto"  # Automatically remove packages on failure

  - type: "file_copy"
    src: "./config.conf"
    dest: "/etc/nginx/nginx.conf"
    rollback: "auto"  # Automatically restore original file
```

#### Manual Rollback Scripts

For complex operations, provide custom rollback scripts:

```yaml
install_steps:
  - type: "custom_script"
    script: "setup_complex_service.sh"
    rollback_script: "teardown_complex_service.sh"

  - type: "ansible_playbook"
    playbook: "deploy_app.yml"
    rollback_playbook: "undeploy_app.yml"
```

#### Conditional Rollback

Use pre-install checks to prevent installation if requirements aren't met:

```yaml
pre_install:
  - type: "script"
    script: "check_disk_space.sh"
  - type: "script"
    script: "check_memory.sh"
  - type: "script"
    script: "check_dependencies.sh"
```

### Best Practices

#### 1. Package Organization

Organize your package files properly:

```
my-webapp/
├── my-webapp.yml          # Main package definition
├── files/                 # Application files
│   ├── app.conf
│   ├── nginx.conf
│   └── scripts/
├── scripts/               # Installation scripts
│   ├── pre_install.sh
│   ├── post_install.sh
│   └── rollback.sh
└── ansible/               # Ansible playbooks
    ├── setup.yml
    └── cleanup.yml
```

#### 2. Error Handling

Always provide proper rollback mechanisms:

```yaml
install_steps:
  # Always specify rollback strategy
  - type: "apt_package"
    action: "install"
    packages: ["nginx"]
    rollback: "remove_packages"  # Explicit rollback

  # Use descriptive step names
  - type: "file_copy"
    src: "./nginx.conf"
    dest: "/etc/nginx/nginx.conf"
    description: "Copy nginx configuration"
    rollback: "restore_original"
```

#### 3. Testing

Test your packages thoroughly:

```bash
# Validate metadata
transactional-installer validate my-webapp.yml

# Test installation in dry-run mode
sudo transactional-installer install my-webapp.yml --dry-run

# Test on a clean system
docker run --rm -v $(pwd):/app transactional-installer install /app/my-webapp.yml
```

#### 4. Monitoring and Logging

Monitor your installations:

```bash
# Check installation logs
tail -f /var/log/transactional-installer/installer.log

# List recent transactions
transactional-installer list

# Get detailed transaction information
transactional-installer status <transaction_id>
```

### Troubleshooting

#### Common Issues

1. **Permission Denied**
   ```bash
   # Ensure you're running as root
   sudo transactional-installer install my-webapp.yml
   ```

2. **Package Validation Fails**
   ```bash
   # Check the validation errors
   transactional-installer validate my-webapp.yml --verbose
   ```

3. **Rollback Fails**
   ```bash
   # Check rollback logs
   grep "rollback" /var/log/transactional-installer/installer.log
   
   # Manual rollback
   sudo transactional-installer rollback <transaction_id>
   ```

4. **Database Connection Issues**
   ```bash
   # Check if database is accessible
   sudo transactional-installer status
   
   # Recreate database if corrupted
   sudo rm /var/lib/transactional-installer/transactions.db
   sudo transactional-installer install my-webapp.yml
   ```

#### Debug Mode

Enable debug logging:

```bash
# Set debug log level
export TRANSACTIONAL_INSTALLER_LOG_LEVEL=DEBUG

# Run with verbose output
sudo transactional-installer install my-webapp.yml --verbose
```

#### Recovery Procedures

1. **Failed Installation Recovery**
   ```bash
   # Check failed transactions
   transactional-installer list --status failed
   
   # Rollback failed transaction
   sudo transactional-installer rollback <transaction_id>
   
   # Clean up and retry
   sudo transactional-installer cleanup --older-than 1
   sudo transactional-installer install my-webapp.yml
   ```

2. **System State Recovery**
   ```bash
   # Check system state
   transactional-installer status <transaction_id>
   
   # Manual system restoration
   sudo apt-get remove <packages>
   sudo systemctl stop <services>
   sudo rm -rf <files>
   ```

### Integration Examples

#### CI/CD Pipeline Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy Application

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          sudo transactional-installer install staging-app.yml
          
      - name: Run tests
        run: |
          curl -f http://staging.example.com/health
          
      - name: Deploy to production
        if: success()
        run: |
          sudo transactional-installer install production-app.yml
```

#### Docker Integration

```dockerfile
# Dockerfile
FROM debian:11

# Install transactional installer
COPY debian_transactional_installer /opt/installer
RUN cd /opt/installer && pip install -e .

# Copy application package
COPY my-webapp.yml /app/my-webapp.yml

# Install application
RUN transactional-installer install /app/my-webapp.yml

# Expose ports
EXPOSE 80 443

# Start services
CMD ["nginx", "-g", "daemon off;"]
```

#### Ansible Integration

```yaml
# ansible/playbook.yml
---
- hosts: webservers
  become: yes
  tasks:
    - name: Install transactional installer
      pip:
        name: /opt/transactional-installer
        state: present
      
    - name: Deploy web application
      command: transactional-installer install /app/my-webapp.yml
      register: install_result
      
    - name: Check installation status
      command: transactional-installer status {{ install_result.stdout }}
      register: status_result
      
    - name: Rollback on failure
      command: transactional-installer rollback {{ install_result.stdout }}
      when: status_result.stdout is search('failed')
```

### Performance Optimization

#### Large Package Installations

For large packages with many files:

```yaml
install_steps:
  # Use batch operations
  - type: "apt_package"
    action: "install"
    packages: ["package1", "package2", "package3"]
    update_cache: false  # Update cache once at the beginning
    
  # Use tar for large file transfers
  - type: "custom_script"
    script: "extract_large_files.sh"
    rollback_script: "remove_large_files.sh"
    
  # Parallel service starts
  - type: "systemd_service"
    service: "service1"
    action: "start"
    
  - type: "systemd_service"
    service: "service2"
    action: "start"
```

#### Database Optimization

```yaml
install_steps:
  # Optimize database operations
  - type: "custom_script"
    script: "optimize_database.sh"
    
  # Use transactions for database changes
  - type: "ansible_playbook"
    playbook: "database_migration.yml"
    vars:
      use_transactions: true
      batch_size: 1000
```

This user guide provides comprehensive coverage of the Debian Transactional Installer's features and usage patterns. For more advanced topics, refer to the API Reference and Architecture documentation.
