# Debian Transactional Installer Documentation

Welcome to the comprehensive documentation for the Debian Transactional Installer. This system provides atomic, transaction-based package installation for Debian-like systems with automatic rollback capabilities.

## Quick Start

### Installation
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

### Basic Usage
```bash
# Create a package template
transactional-installer create-template my-app 1.0.0 -o my-app.yml

# Validate the package
transactional-installer validate my-app.yml

# Install the package
sudo transactional-installer install my-app.yml
```

## Documentation Sections

### 📖 [User Guide](user-guide.md)
Complete user guide with step-by-step instructions, best practices, and troubleshooting.

**Topics covered:**
- Getting started with installation
- Basic and advanced usage patterns
- Complex installation scenarios
- Rollback strategies
- Best practices
- Troubleshooting common issues
- Integration examples

### 🏗️ [Architecture](architecture.md)
Detailed system architecture and design documentation.

**Topics covered:**
- System overview and components
- Core modules and their responsibilities
- Storage architecture and database schema
- Security architecture
- Error handling and recovery
- Performance considerations
- Scalability and deployment options

### 📚 [API Reference](api-reference.md)
Complete API documentation for all modules and functions.

**Topics covered:**
- Core modules (TransactionManager, StateTracker, RollbackEngine)
- Backend modules (StepExecutor, AnsibleBackend, SimpleHandlers)
- Storage modules (TransactionDB)
- Metadata modules (MetadataParser)
- CLI interface
- Exception handling

### 💡 [Examples](examples.md)
Comprehensive examples for various use cases and scenarios.

**Examples included:**
- Simple web server installation
- Python web application with Flask
- Full-stack application with database
- Microservices platform
- CI/CD pipeline integration
- Docker integration
- Ansible integration
- Testing examples

## Key Features

### 🔄 Transactional Installation
- **Atomic Operations**: Either all changes succeed or the system is rolled back
- **ACID Compliance**: Database transactions with WAL mode
- **Automatic Rollback**: Failed installations automatically restore previous state

### 🛡️ Safety & Security
- **Input Validation**: JSON Schema validation for all metadata
- **Path Traversal Protection**: Secure file operations
- **Privilege Management**: Root privileges only when needed
- **Audit Trail**: Comprehensive logging and transaction history

### 🔧 Flexibility
- **Multiple Step Types**: APT packages, file operations, custom scripts, Ansible playbooks
- **Custom Rollback Strategies**: Automatic, manual, or Ansible-based rollback
- **Extensible Architecture**: Easy to add new step types and handlers

### 🐳 Container Support
- **Docker Integration**: Works in containers with proper volume mounting
- **Isolation**: Process and filesystem isolation
- **Portability**: Consistent behavior across environments

## System Requirements

### Minimum Requirements
- **OS**: Debian 11+ or Ubuntu 20.04+
- **Memory**: 256MB RAM
- **Disk Space**: 500MB free space
- **Python**: 3.9+

### Recommended Requirements
- **OS**: Debian 11+ or Ubuntu 22.04+
- **Memory**: 1GB+ RAM
- **Disk Space**: 2GB+ free space
- **Python**: 3.11+

## Installation Methods

### From Source
```bash
git clone https://github.com/your-org/debian_transactional_installer.git
cd debian_transactional_installer
pip install -e .
```

### Using Docker
```bash
docker build -t transactional-installer .
docker run --privileged -v /var/lib/transactional-installer:/var/lib/transactional-installer transactional-installer
```

### Using Package Manager
```bash
# Add repository and install (when available)
sudo apt update
sudo apt install transactional-installer
```

## Quick Examples

### Simple Package Installation
```yaml
package:
  name: "my-app"
  version: "1.0.0"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx"]
    rollback: "remove_packages"

  - type: "file_copy"
    src: "./app.conf"
    dest: "/etc/nginx/app.conf"
    rollback: "restore_original"
```

### Web Application with Database
```yaml
package:
  name: "webapp"
  version: "2.0.0"

install_steps:
  - type: "apt_package"
    action: "install"
    packages: ["nginx", "postgresql", "python3"]
    rollback: "remove_packages"

  - type: "ansible_playbook"
    playbook: "setup_database.yml"
    rollback_playbook: "cleanup_database.yml"

  - type: "systemd_service"
    service: "nginx"
    action: "restart"
    rollback: "stop"
```

## Common Commands

### Package Management
```bash
# Install a package
sudo transactional-installer install package.yml

# Validate package without installing
sudo transactional-installer install package.yml --dry-run

# Rollback a transaction
sudo transactional-installer rollback <transaction_id>
```

### Transaction Management
```bash
# List recent transactions
transactional-installer list

# Get transaction status
transactional-installer status <transaction_id>

# Clean up old transactions
transactional-installer cleanup --older-than 30
```

### Package Development
```bash
# Create a template
transactional-installer create-template my-app 1.0.0 -o my-app.yml

# Validate metadata
transactional-installer validate package.yml
```

## Testing

### Run All Tests
```bash
# Run unit and integration tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=backends --cov=storage --cov=metadata --cov=cli
```

### Test Specific Components
```bash
# Test transaction manager
pytest tests/test_transaction_manager.py -v

# Test integration scenarios
pytest tests/test_integration_demo_stack.py -v

# Test metadata parsing
pytest tests/test_metadata_parser.py -v
```

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
flake8 core/ backends/ storage/ metadata/ cli/ tests/
mypy core/ backends/ storage/ metadata/ cli/
```

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features

### Testing Guidelines
- Write unit tests for all new functionality
- Include integration tests for complex scenarios
- Ensure test coverage remains high
- Test rollback scenarios thoroughly

## Support

### Getting Help
- **Documentation**: Start with the [User Guide](user-guide.md)
- **Examples**: Check the [Examples](examples.md) for common use cases
- **API Reference**: Consult the [API Reference](api-reference.md) for technical details
- **Issues**: Report bugs and request features on GitHub

### Community
- **Discussions**: Join GitHub Discussions for questions and ideas
- **Contributions**: Submit pull requests for improvements
- **Feedback**: Share your experience and suggestions

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](../LICENSE) file for details.

## Version History

### Current Version: 1.0.0
- Initial release with core transactional installation capabilities
- Support for APT packages, file operations, and custom scripts
- Automatic rollback functionality
- SQLite-based transaction storage
- Comprehensive test suite

### Roadmap
- **v1.1.0**: Enhanced Ansible integration
- **v1.2.0**: Kubernetes operator support
- **v1.3.0**: Distributed transaction support
- **v2.0.0**: Major architecture improvements

---

**Need help?** Start with the [User Guide](user-guide.md) or check the [Examples](examples.md) for practical use cases.
