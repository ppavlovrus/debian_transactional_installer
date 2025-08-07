# Examples

This document provides comprehensive examples of using the Debian Transactional Installer for various real-world scenarios.

## Basic Examples

### 1. Simple Web Server

A basic example of installing a simple web server with nginx.

**File: `examples/simple-web-server.yml`**
```yaml
package:
  name: "simple-web-server"
  version: "1.0.0"
  description: "A simple web server with nginx"
  author: "Your Name"
  license: "MIT"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx"]
    rollback: "remove_packages"

  - type: "file_copy"
    src: "./index.html"
    dest: "/var/www/html/index.html"
    owner: "www-data"
    group: "www-data"
    mode: "644"
    rollback: "restore_original"

  - type: "systemd_service"
    service: "nginx"
    action: "enable"
    rollback: "disable"

  - type: "systemd_service"
    service: "nginx"
    action: "start"
    rollback: "stop"

requirements:
  min_memory: 256
  min_disk_space: 500
  os_version: "11.0"
```

**File: `examples/index.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Simple Web Server</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a simple web server installed using the transactional installer.</p>
</body>
</html>
```

**Installation:**
```bash
# Create the package
transactional-installer create-template simple-web-server 1.0.0 -o simple-web-server.yml

# Copy the index.html file
cp examples/index.html .

# Install the package
sudo transactional-installer install simple-web-server.yml
```

### 2. Python Web Application

A more complex example with a Python web application using Flask.

**File: `examples/python-webapp.yml`**
```yaml
package:
  name: "python-webapp"
  version: "1.0.0"
  description: "Python web application with Flask"
  author: "Your Name"
  license: "MIT"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["python3", "python3-pip", "python3-venv", "nginx"]
    rollback: "remove_packages"

  - type: "user_management"
    username: "webapp"
    action: "create"
    user_data:
      home: "/var/www/webapp"
      shell: "/bin/bash"
      groups: ["www-data"]
    rollback: "remove_user"

  - type: "file_copy"
    src: "./app/"
    dest: "/var/www/webapp/"
    owner: "webapp"
    group: "www-data"
    mode: "755"
    rollback: "restore_original"

  - type: "custom_script"
    script: "setup_python_env.sh"
    rollback_script: "cleanup_python_env.sh"

  - type: "file_copy"
    src: "./nginx/webapp.conf"
    dest: "/etc/nginx/sites-available/webapp.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  - type: "custom_script"
    script: "enable_nginx_site.sh"
    rollback_script: "disable_nginx_site.sh"

  - type: "file_copy"
    src: "./systemd/webapp.service"
    dest: "/etc/systemd/system/webapp.service"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  - type: "systemd_service"
    service: "webapp"
    action: "enable"
    rollback: "disable"

  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "webapp"
    action: "start"
    rollback: "stop"

requirements:
  min_memory: 512
  min_disk_space: 1000
  os_version: "11.0"
```

**File: `examples/app/app.py`**
```python
from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**File: `examples/app/requirements.txt`**
```
Flask==2.3.3
Werkzeug==2.3.7
```

**File: `examples/app/templates/index.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Python Web App</title>
</head>
<body>
    <h1>Welcome to Python Web App</h1>
    <p>This application was installed using the transactional installer.</p>
</body>
</html>
```

**File: `examples/scripts/setup_python_env.sh`**
```bash
#!/bin/bash
set -e

# Create virtual environment
python3 -m venv /var/www/webapp/venv

# Activate virtual environment and install dependencies
source /var/www/webapp/venv/bin/activate
pip install -r /var/www/webapp/requirements.txt

# Set proper permissions
chown -R webapp:www-data /var/www/webapp
chmod -R 755 /var/www/webapp
```

**File: `examples/scripts/cleanup_python_env.sh`**
```bash
#!/bin/bash
set -e

# Remove virtual environment
rm -rf /var/www/webapp/venv

# Remove application files
rm -rf /var/www/webapp/app
```

**File: `examples/nginx/webapp.conf`**
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**File: `examples/systemd/webapp.service`**
```ini
[Unit]
Description=Python Web Application
After=network.target

[Service]
Type=simple
User=webapp
WorkingDirectory=/var/www/webapp
Environment=PATH=/var/www/webapp/venv/bin
ExecStart=/var/www/webapp/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Advanced Examples

### 3. Full-Stack Application with Database

A complete full-stack application with PostgreSQL database.

**File: `examples/fullstack-app.yml`**
```yaml
package:
  name: "fullstack-app"
  version: "2.0.0"
  description: "Full-stack web application with PostgreSQL"
  author: "Your Name"
  license: "MIT"

install_steps:
  # Install system packages
  - type: "apt_package"
    action: "install"
    packages: ["nginx", "postgresql", "postgresql-contrib", "python3", "python3-pip", "python3-venv"]
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

  # Create application directory
  - type: "custom_script"
    script: "create_app_directory.sh"
    rollback_script: "remove_app_directory.sh"

  # Copy application files
  - type: "file_copy"
    src: "./app/"
    dest: "/var/www/fullstack-app/"
    owner: "appuser"
    group: "www-data"
    mode: "755"
    rollback: "restore_original"

  # Setup Python environment
  - type: "custom_script"
    script: "setup_python_env.sh"
    rollback_script: "cleanup_python_env.sh"

  # Setup database
  - type: "ansible_playbook"
    playbook: "setup_database.yml"
    rollback_playbook: "cleanup_database.yml"
    vars:
      db_name: "fullstackapp"
      db_user: "appuser"
      db_password: "secure_password"

  # Copy nginx configuration
  - type: "file_copy"
    src: "./nginx/fullstack-app.conf"
    dest: "/etc/nginx/sites-available/fullstack-app.conf"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  # Enable nginx site
  - type: "custom_script"
    script: "enable_nginx_site.sh"
    rollback_script: "disable_nginx_site.sh"

  # Copy systemd service
  - type: "file_copy"
    src: "./systemd/fullstack-app.service"
    dest: "/etc/systemd/system/fullstack-app.service"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  # Start services
  - type: "systemd_service"
    service: "postgresql"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "fullstack-app"
    action: "enable"
    rollback: "disable"

  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "fullstack-app"
    action: "start"
    rollback: "stop"

pre_install:
  - type: "script"
    script: "check_system_requirements.sh"

post_install:
  - type: "script"
    script: "post_install_setup.sh"

requirements:
  min_memory: 2048
  min_disk_space: 5000
  os_version: "11.0"
```

**File: `examples/ansible/setup_database.yml`**
```yaml
---
- hosts: localhost
  become: yes
  tasks:
    - name: Create database
      postgresql_db:
        name: "{{ db_name }}"
        state: present

    - name: Create database user
      postgresql_user:
        db: "{{ db_name }}"
        name: "{{ db_user }}"
        password: "{{ db_password }}"
        priv: "ALL"
        state: present

    - name: Create tables
      postgresql_query:
        db: "{{ db_name }}"
        query: |
          CREATE TABLE IF NOT EXISTS users (
              id SERIAL PRIMARY KEY,
              username VARCHAR(50) UNIQUE NOT NULL,
              email VARCHAR(100) UNIQUE NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
```

**File: `examples/ansible/cleanup_database.yml`**
```yaml
---
- hosts: localhost
  become: yes
  tasks:
    - name: Drop database
      postgresql_db:
        name: "{{ db_name }}"
        state: absent

    - name: Drop database user
      postgresql_user:
        name: "{{ db_user }}"
        state: absent
```

### 4. Microservices Platform

A complex microservices platform with multiple services.

**File: `examples/microservices-platform.yml`**
```yaml
package:
  name: "microservices-platform"
  version: "1.0.0"
  description: "Microservices platform with multiple services"
  author: "Your Name"
  license: "MIT"

install_steps:
  # Install base dependencies
  - type: "apt_package"
    action: "install"
    packages: ["docker.io", "docker-compose", "nginx", "redis-server", "python3", "python3-pip"]
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

  - type: "user_management"
    username: "worker-service"
    action: "create"
    user_data:
      home: "/home/worker-service"
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

  # Enable nginx site
  - type: "custom_script"
    script: "enable_nginx_site.sh"
    rollback_script: "disable_nginx_site.sh"

  # Start services
  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "redis"
    action: "restart"
    rollback: "stop"

  - type: "systemd_service"
    service: "docker"
    action: "restart"
    rollback: "stop"

requirements:
  min_memory: 4096
  min_disk_space: 10000
  os_version: "11.0"
```

**File: `examples/services/docker-compose.yml`**
```yaml
version: '3.8'

services:
  api-service:
    image: api-service:latest
    container_name: api-service
    networks:
      - microservices-network
    environment:
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    ports:
      - "8001:8001"

  web-service:
    image: web-service:latest
    container_name: web-service
    networks:
      - microservices-network
    environment:
      - API_SERVICE_URL=http://api-service:8001
    ports:
      - "8002:8002"

  worker-service:
    image: worker-service:latest
    container_name: worker-service
    networks:
      - microservices-network
    environment:
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:pass@db:5432/app

  redis:
    image: redis:alpine
    container_name: redis
    networks:
      - microservices-network
    ports:
      - "6379:6379"

  db:
    image: postgres:13
    container_name: postgres
    networks:
      - microservices-network
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    ports:
      - "5432:5432"

networks:
  microservices-network:
    driver: bridge
```

**File: `examples/nginx/microservices.conf`**
```nginx
upstream api_service {
    server 127.0.0.1:8001;
}

upstream web_service {
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://api_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://web_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Integration Examples

### 5. CI/CD Pipeline Integration

**File: `.github/workflows/deploy.yml`**
```yaml
name: Deploy Application

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          pytest tests/
          
      - name: Build Docker images
        run: |
          docker build -t api-service:latest ./api-service
          docker build -t web-service:latest ./web-service
          docker build -t worker-service:latest ./worker-service

  deploy-staging:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          sudo transactional-installer install staging-app.yml
          
      - name: Run health checks
        run: |
          curl -f http://staging.example.com/health
          curl -f http://staging.example.com/api/health
          
      - name: Run integration tests
        run: |
          pytest integration_tests/ --url=http://staging.example.com

  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, deploy-staging]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          sudo transactional-installer install production-app.yml
          
      - name: Run health checks
        run: |
          curl -f http://production.example.com/health
          curl -f http://production.example.com/api/health
          
      - name: Notify deployment
        run: |
          curl -X POST $SLACK_WEBHOOK_URL \
            -H 'Content-type: application/json' \
            -d '{"text":"Production deployment completed successfully!"}'
```

### 6. Docker Integration

**File: `Dockerfile`**
```dockerfile
FROM debian:11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sqlite3 \
    ansible \
    && rm -rf /var/lib/apt/lists/*

# Install transactional installer
COPY . /opt/transactional-installer
WORKDIR /opt/transactional-installer
RUN pip install -e .

# Copy application package
COPY examples/fullstack-app.yml /app/fullstack-app.yml
COPY examples/app/ /app/app/
COPY examples/scripts/ /app/scripts/
COPY examples/ansible/ /app/ansible/
COPY examples/nginx/ /app/nginx/
COPY examples/systemd/ /app/systemd/

# Install application
RUN transactional-installer install /app/fullstack-app.yml

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Start services
CMD ["nginx", "-g", "daemon off;"]
```

### 7. Ansible Integration

**File: `ansible/deploy.yml`**
```yaml
---
- hosts: webservers
  become: yes
  tasks:
    - name: Install transactional installer
      pip:
        name: /opt/transactional-installer
        state: present
      
    - name: Copy application files
      copy:
        src: "{{ item }}"
        dest: "/app/"
        mode: "0644"
      loop:
        - "fullstack-app.yml"
        - "app/"
        - "scripts/"
        - "ansible/"
        - "nginx/"
        - "systemd/"
      
    - name: Deploy application
      command: transactional-installer install /app/fullstack-app.yml
      register: install_result
      
    - name: Check installation status
      command: transactional-installer status {{ install_result.stdout }}
      register: status_result
      
    - name: Rollback on failure
      command: transactional-installer rollback {{ install_result.stdout }}
      when: status_result.stdout is search('failed')
      
    - name: Wait for services to be ready
      wait_for:
        port: "{{ item }}"
        timeout: 60
      loop:
        - 80
        - 8001
        - 8002
      
    - name: Run health checks
      uri:
        url: "http://{{ inventory_hostname }}/health"
        status_code: 200
      register: health_check
      
    - name: Fail if health check fails
      fail:
        msg: "Health check failed"
      when: health_check.status != 200
```

## Testing Examples

### 8. Test Package

A package specifically designed for testing the installer.

**File: `examples/test-package.yml`**
```yaml
package:
  name: "test-package"
  version: "1.0.0"
  description: "Package for testing the transactional installer"
  author: "Test User"
  license: "MIT"

install_steps:
  # Test package installation
  - type: "apt_package"
    action: "install"
    packages: ["curl", "wget"]
    rollback: "remove_packages"

  # Test file operations
  - type: "file_copy"
    src: "./test-files/test.txt"
    dest: "/tmp/test-installed.txt"
    owner: "root"
    group: "root"
    mode: "644"
    rollback: "restore_original"

  # Test user creation
  - type: "user_management"
    username: "testuser"
    action: "create"
    user_data:
      home: "/home/testuser"
      shell: "/bin/bash"
      groups: ["users"]
    rollback: "remove_user"

  # Test custom script
  - type: "custom_script"
    script: "test_script.sh"
    rollback_script: "test_rollback.sh"

  # Test service management
  - type: "systemd_service"
    service: "ssh"
    action: "restart"
    rollback: "restart"

pre_install:
  - type: "script"
    script: "pre_install_test.sh"

post_install:
  - type: "script"
    script: "post_install_test.sh"

requirements:
  min_memory: 256
  min_disk_space: 100
  os_version: "11.0"
```

**File: `examples/test-files/test.txt`**
```
This is a test file for the transactional installer.
It should be copied during installation and removed during rollback.
```

**File: `examples/scripts/test_script.sh`**
```bash
#!/bin/bash
set -e

echo "Running test script..."
echo "Test completed successfully" > /tmp/test-script-output.txt
```

**File: `examples/scripts/test_rollback.sh`**
```bash
#!/bin/bash
set -e

echo "Running test rollback script..."
rm -f /tmp/test-script-output.txt
```

### 9. Rollback Test Package

A package designed to test rollback functionality.

**File: `examples/rollback-test.yml`**
```yaml
package:
  name: "rollback-test"
  version: "1.0.0"
  description: "Package for testing rollback functionality"
  author: "Test User"
  license: "MIT"

install_steps:
  # Step 1: Install packages (should succeed)
  - type: "apt_package"
    action: "install"
    packages: ["curl"]
    rollback: "remove_packages"

  # Step 2: Copy file (should succeed)
  - type: "file_copy"
    src: "./test-files/step2.txt"
    dest: "/tmp/step2.txt"
    rollback: "restore_original"

  # Step 3: Create user (should succeed)
  - type: "user_management"
    username: "rollbackuser"
    action: "create"
    user_data:
      home: "/home/rollbackuser"
      shell: "/bin/bash"
    rollback: "remove_user"

  # Step 4: Custom script that fails (should trigger rollback)
  - type: "custom_script"
    script: "failing_script.sh"
    rollback_script: "cleanup_after_failure.sh"

requirements:
  min_memory: 256
  min_disk_space: 100
  os_version: "11.0"
```

**File: `examples/scripts/failing_script.sh`**
```bash
#!/bin/bash
set -e

echo "This script is designed to fail..."
echo "Creating a file that should be cleaned up during rollback..."
echo "test content" > /tmp/failing-script-file.txt

# Intentionally fail
exit 1
```

**File: `examples/scripts/cleanup_after_failure.sh`**
```bash
#!/bin/bash
set -e

echo "Cleaning up after script failure..."
rm -f /tmp/failing-script-file.txt
```

## Usage Instructions

### Running the Examples

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/debian_transactional_installer.git
   cd debian_transactional_installer
   ```

2. **Install the transactional installer:**
   ```bash
   pip install -e .
   ```

3. **Navigate to examples directory:**
   ```bash
   cd examples
   ```

4. **Run a simple example:**
   ```bash
   # Test the simple web server
   sudo transactional-installer install simple-web-server.yml
   
   # Check if it's working
   curl http://localhost
   ```

5. **Test rollback functionality:**
   ```bash
   # Install the rollback test package
   sudo transactional-installer install rollback-test.yml
   
   # Check that rollback occurred
   sudo transactional-installer list
   ```

### Customizing Examples

1. **Modify package metadata:**
   - Change package name, version, and description
   - Update author and license information

2. **Add or remove installation steps:**
   - Add new package installations
   - Include additional file operations
   - Add custom scripts

3. **Customize rollback strategies:**
   - Change rollback methods for specific steps
   - Add custom rollback scripts

4. **Update requirements:**
   - Modify memory and disk space requirements
   - Change OS version requirements

### Best Practices for Examples

1. **Always test in a safe environment first**
2. **Use dry-run mode before actual installation**
3. **Keep examples simple and focused**
4. **Include proper error handling**
5. **Document any external dependencies**
6. **Provide cleanup instructions**

These examples demonstrate the full range of capabilities of the Debian Transactional Installer and provide a solid foundation for creating your own packages.
