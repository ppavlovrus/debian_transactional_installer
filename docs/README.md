# Documentation

This directory contains comprehensive documentation for the Debian Transactional Installer project.

## Documentation Structure

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

### 🏠 [Index](index.md)
Main documentation index with overview and navigation.

## Building Documentation

### Prerequisites
- [pandoc](https://pandoc.org/installing.html) for converting markdown to HTML

### Build Commands

```bash
# Build HTML documentation
make docs

# Build and serve documentation locally
make docs-serve

# Or use the script directly
./scripts/build-docs.sh
```

### Manual Build
```bash
# Install pandoc (Ubuntu/Debian)
sudo apt-get install pandoc

# Build documentation
./scripts/build-docs.sh

# Serve locally
cd docs/build && python3 -m http.server 8000
```

## Documentation Standards

### Writing Guidelines
- Use clear, concise language
- Include code examples where appropriate
- Follow consistent formatting
- Use proper markdown syntax
- Include cross-references between documents

### Code Examples
- Use syntax highlighting for code blocks
- Include complete, working examples
- Provide both simple and complex scenarios
- Include error handling examples

### Structure
- Use consistent heading hierarchy
- Include table of contents for long documents
- Use descriptive section names
- Include navigation between related sections

## Contributing to Documentation

### Adding New Documentation
1. Create a new markdown file in the `docs/` directory
2. Follow the existing naming conventions
3. Update the main index file to include the new document
4. Add appropriate cross-references
5. Test the build process

### Updating Existing Documentation
1. Maintain the existing structure and style
2. Update cross-references if needed
3. Test the build process
4. Update the table of contents if necessary

### Documentation Review
- Ensure all links work correctly
- Verify code examples are accurate
- Check for consistency in terminology
- Test the build process
- Review for clarity and completeness

## Documentation Tools

### Required Tools
- **pandoc**: Markdown to HTML conversion
- **Python 3**: For serving documentation locally
- **Git**: For version control

### Optional Tools
- **Markdown editors**: VS Code, Typora, etc.
- **Markdown linters**: markdownlint
- **Spell checkers**: For proofreading

## Documentation Workflow

### Development Workflow
1. Write documentation in markdown
2. Test locally with `make docs-serve`
3. Review in browser
4. Commit changes
5. Push to repository

### Release Workflow
1. Update version numbers in documentation
2. Review all documentation for accuracy
3. Build final documentation
4. Include in release artifacts
5. Update external references

## Maintenance

### Regular Tasks
- Review and update outdated information
- Check for broken links
- Update examples to match current code
- Review user feedback and issues
- Update installation instructions

### Quality Assurance
- Test all code examples
- Verify command-line instructions
- Check formatting consistency
- Review for technical accuracy
- Ensure accessibility standards

## Support

For questions about the documentation:
- Check existing documentation first
- Review the examples for similar use cases
- Open an issue on GitHub
- Join community discussions

---

**Note**: This documentation is maintained alongside the code. Please ensure documentation stays up-to-date with code changes.
