"""Main CLI interface for TransactionalInstaller."""

import sys
import logging
import click
from pathlib import Path
import os

from core.transaction_manager import TransactionManager
from metadata.metadata_parser import MetadataParser
from core.exceptions import TransactionalInstallerError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/transactional-installer/installer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output')
@click.pass_context
def cli(ctx, verbose, quiet):
    """TransactionalInstaller - MSI-like transactional installer for Debian systems."""
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set log level based on options
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Check if running as root
    if not _check_root_privileges():
        click.echo("Error: This tool requires root privileges.", err=True)
        sys.exit(1)


@cli.command()
@click.argument('package_file', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Validate package without installing')
@click.option('--force', is_flag=True, help='Force installation even if validation fails')
@click.pass_context
def install(ctx, package_file, dry_run, force):
    """Install a package from metadata file."""
    try:
        # Parse metadata
        parser = MetadataParser()
        metadata = parser.parse_file(package_file)
        
        package_info = parser.get_package_info(metadata)
        install_steps = parser.get_install_steps(metadata)
        
        click.echo(f"Installing package: {package_info['name']} v{package_info['version']}")
        
        if dry_run:
            click.echo("Dry run mode - validating package only")
            _validate_package(metadata, parser)
            click.echo("Package validation successful")
            return
        
        # Initialize transaction manager
        manager = TransactionManager()
        
        # Begin transaction
        transaction_id = manager.begin_transaction(
            package_name=package_info['name'],
            metadata=metadata
        )
        
        click.echo(f"Started transaction: {transaction_id}")
        
        try:
            # Execute installation steps
            manager.execute_steps(install_steps)
            
            # Commit transaction
            manager.commit_transaction()
            
            click.echo(f"Package {package_info['name']} installed successfully")
            
        except Exception as e:
            click.echo(f"Installation failed: {e}", err=True)
            click.echo("Rolling back changes...")
            
            try:
                manager.rollback_transaction()
                click.echo("Rollback completed successfully")
            except Exception as rollback_error:
                click.echo(f"Rollback failed: {rollback_error}", err=True)
            
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('transaction_id', type=int)
@click.pass_context
def rollback(ctx, transaction_id):
    """Rollback a specific transaction."""
    try:
        manager = TransactionManager()
        
        # Get transaction status
        status = manager.get_transaction_status(transaction_id)
        
        if status['status'] == 'completed':
            click.echo(f"Transaction {transaction_id} is already completed. Cannot rollback.")
            sys.exit(1)
        
        click.echo(f"Rolling back transaction {transaction_id}...")
        
        # Get transaction steps and perform rollback
        steps = manager.db.get_transaction_steps(transaction_id)
        manager.rollback_engine.execute_rollback(transaction_id, steps)
        
        click.echo(f"Transaction {transaction_id} rolled back successfully")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--limit', default=50, help='Maximum number of transactions to show')
@click.pass_context
def list(ctx, limit):
    """List recent transactions."""
    try:
        manager = TransactionManager()
        transactions = manager.list_transactions(limit)
        
        if not transactions:
            click.echo("No transactions found.")
            return
        
        click.echo(f"{'ID':<8} {'Package':<20} {'Status':<15} {'Created':<20}")
        click.echo("-" * 70)
        
        for tx in transactions:
            click.echo(f"{tx['id']:<8} {tx['package_name']:<20} {tx['status']:<15} {tx['created_at']:<20}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--older-than', default=30, help='Remove transactions older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned up without doing it')
@click.pass_context
def cleanup(ctx, older_than, dry_run):
    """Clean up old transactions."""
    try:
        manager = TransactionManager()
        
        if dry_run:
            # This would need to be implemented to show what would be cleaned
            click.echo(f"Would clean up transactions older than {older_than} days")
            return
        
        count = manager.cleanup_old_transactions(older_than)
        click.echo(f"Cleaned up {count} old transactions")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('package_name')
@click.argument('version')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def create_template(ctx, package_name, version, output):
    """Create a metadata template for a new package."""
    try:
        parser = MetadataParser()
        template = parser.create_metadata_template(package_name, version)
        
        if output:
            parser.save_metadata(template, output)
            click.echo(f"Template saved to: {output}")
        else:
            import yaml
            click.echo(yaml.dump(template, default_flow_style=False, indent=2))
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('package_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, package_file):
    """Validate a package metadata file."""
    try:
        parser = MetadataParser()
        metadata = parser.parse_file(package_file)
        
        package_info = parser.get_package_info(metadata)
        install_steps = parser.get_install_steps(metadata)
        
        click.echo(f"Package: {package_info['name']} v{package_info['version']}")
        click.echo(f"Installation steps: {len(install_steps)}")
        
        # Validate each step
        for i, step in enumerate(install_steps, 1):
            step_type = step.get('type', 'unknown')
            click.echo(f"  Step {i}: {step_type}")
        
        click.echo("Package validation successful")
        
    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and health."""
    try:
        click.echo("TransactionalInstaller Status")
        click.echo("=" * 30)
        
        # Check database
        try:
            manager = TransactionManager()
            recent_txs = manager.list_transactions(5)
            click.echo(f"Database: OK ({len(recent_txs)} recent transactions)")
        except Exception as e:
            click.echo(f"Database: ERROR ({e})")
        
        # Check directories
        dirs_to_check = [
            '/var/lib/transactional-installer',
            '/var/log/transactional-installer',
            '/etc/transactional-installer'
        ]
        
        for dir_path in dirs_to_check:
            if Path(dir_path).exists():
                click.echo(f"Directory {dir_path}: OK")
            else:
                click.echo(f"Directory {dir_path}: MISSING")
        
        # Check root privileges
        if _check_root_privileges():
            click.echo("Root privileges: OK")
        else:
            click.echo("Root privileges: ERROR")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _check_root_privileges() -> bool:
    """Check if the script is running with root privileges."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows doesn't have geteuid
        return True


def _validate_package(metadata: dict, parser: MetadataParser) -> None:
    """Validate a package without installing it."""
    # Validate metadata structure
    parser.validate_metadata(metadata)
    
    # Extract and validate components
    package_info = parser.get_package_info(metadata)
    install_steps = parser.get_install_steps(metadata)
    
    # Validate each step
    for step in install_steps:
        parser.validate_step(step)
    
    # Check dependencies
    dependencies = parser.get_dependencies(metadata)
    if dependencies:
        click.echo(f"Dependencies: {', '.join(dependencies)}")
    
    # Check conflicts
    conflicts = parser.get_conflicts(metadata)
    if conflicts:
        click.echo(f"Conflicts: {', '.join(conflicts)}")
    
    # Check requirements
    requirements = parser.get_requirements(metadata)
    if requirements:
        click.echo(f"Requirements: {requirements}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main() 