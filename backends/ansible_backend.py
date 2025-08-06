"""Ansible backend for complex installation operations."""

import os
import tempfile
import logging
from typing import Dict, Any, Optional

try:
    import ansible_runner
except ImportError:
    ansible_runner = None

from core.exceptions import StepExecutionError


logger = logging.getLogger(__name__)


class AnsibleBackend:
    """Backend for executing Ansible playbooks."""

    def __init__(self, playbook_dir: str = "/etc/transactional-installer/ansible"):
        """Initialize Ansible backend.

        Args:
            playbook_dir: Directory containing Ansible playbooks
        """
        self.playbook_dir = playbook_dir
        
        if not ansible_runner:
            logger.warning("ansible-runner not available. Ansible operations will fail.")
        
        # Ensure playbook directory exists
        os.makedirs(playbook_dir, exist_ok=True)

    def run_playbook(self, playbook: str, vars_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run an Ansible playbook.

        Args:
            playbook: Path to the playbook file
            vars_data: Variables to pass to the playbook

        Returns:
            Playbook execution result

        Raises:
            StepExecutionError: If playbook execution fails
        """
        if not ansible_runner:
            raise StepExecutionError("ansible-runner not available")

        try:
            logger.info(f"Running Ansible playbook: {playbook}")
            
            # Resolve playbook path
            playbook_path = self._resolve_playbook_path(playbook)
            if not os.path.exists(playbook_path):
                raise StepExecutionError(f"Playbook not found: {playbook_path}")
            
            # Prepare variables
            extra_vars = vars_data or {}
            
            # Create temporary directory for Ansible artifacts
            with tempfile.TemporaryDirectory() as temp_dir:
                # Run the playbook
                result = ansible_runner.run(
                    playbook=playbook_path,
                    extravars=extra_vars,
                    private_data_dir=temp_dir,
                    json_mode=True
                )
                
                # Check execution result
                if result.rc != 0:
                    logger.error(f"Ansible playbook failed with rc={result.rc}")
                    logger.error(f"Playbook output: {result.stdout.read() if result.stdout else 'No output'}")
                    raise StepExecutionError(f"Ansible playbook failed with rc={result.rc}")
                
                return {
                    "success": True,
                    "playbook": playbook,
                    "vars": extra_vars,
                    "rc": result.rc,
                    "stats": result.stats
                }
                
        except Exception as e:
            logger.error(f"Ansible playbook execution failed: {e}")
            raise StepExecutionError(f"Ansible playbook execution failed: {e}")

    def run_playbook_with_inventory(self, playbook: str, inventory: str, 
                                  vars_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run an Ansible playbook with custom inventory.

        Args:
            playbook: Path to the playbook file
            inventory: Path to inventory file or inventory string
            vars_data: Variables to pass to the playbook

        Returns:
            Playbook execution result

        Raises:
            StepExecutionError: If playbook execution fails
        """
        if not ansible_runner:
            raise StepExecutionError("ansible-runner not available")

        try:
            logger.info(f"Running Ansible playbook with inventory: {playbook}")
            
            # Resolve playbook path
            playbook_path = self._resolve_playbook_path(playbook)
            if not os.path.exists(playbook_path):
                raise StepExecutionError(f"Playbook not found: {playbook_path}")
            
            # Prepare variables
            extra_vars = vars_data or {}
            
            # Create temporary directory for Ansible artifacts
            with tempfile.TemporaryDirectory() as temp_dir:
                # Run the playbook with inventory
                result = ansible_runner.run(
                    playbook=playbook_path,
                    inventory=inventory,
                    extravars=extra_vars,
                    private_data_dir=temp_dir,
                    json_mode=True
                )
                
                # Check execution result
                if result.rc != 0:
                    logger.error(f"Ansible playbook failed with rc={result.rc}")
                    logger.error(f"Playbook output: {result.stdout.read() if result.stdout else 'No output'}")
                    raise StepExecutionError(f"Ansible playbook failed with rc={result.rc}")
                
                return {
                    "success": True,
                    "playbook": playbook,
                    "inventory": inventory,
                    "vars": extra_vars,
                    "rc": result.rc,
                    "stats": result.stats
                }
                
        except Exception as e:
            logger.error(f"Ansible playbook execution failed: {e}")
            raise StepExecutionError(f"Ansible playbook execution failed: {e}")

    def validate_playbook(self, playbook: str) -> bool:
        """Validate an Ansible playbook.

        Args:
            playbook: Path to the playbook file

        Returns:
            True if playbook is valid
        """
        try:
            playbook_path = self._resolve_playbook_path(playbook)
            
            if not os.path.exists(playbook_path):
                logger.error(f"Playbook not found: {playbook_path}")
                return False
            
            # Basic YAML validation could be added here
            # For now, just check if file exists and is readable
            with open(playbook_path, 'r') as f:
                f.read()
            
            return True
            
        except Exception as e:
            logger.error(f"Playbook validation failed: {e}")
            return False

    def list_playbooks(self) -> list:
        """List available playbooks.

        Returns:
            List of available playbook paths
        """
        playbooks = []
        
        try:
            if os.path.exists(self.playbook_dir):
                for file in os.listdir(self.playbook_dir):
                    if file.endswith('.yml') or file.endswith('.yaml'):
                        playbooks.append(file)
                        
        except Exception as e:
            logger.error(f"Failed to list playbooks: {e}")
            
        return playbooks

    def create_playbook(self, name: str, content: str) -> str:
        """Create a new playbook file.

        Args:
            name: Name of the playbook file
            content: Playbook content

        Returns:
            Path to created playbook

        Raises:
            StepExecutionError: If creation fails
        """
        try:
            # Ensure file has .yml extension
            if not name.endswith('.yml') and not name.endswith('.yaml'):
                name += '.yml'
            
            playbook_path = os.path.join(self.playbook_dir, name)
            
            with open(playbook_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Created playbook: {playbook_path}")
            return playbook_path
            
        except Exception as e:
            logger.error(f"Failed to create playbook: {e}")
            raise StepExecutionError(f"Failed to create playbook: {e}")

    def _resolve_playbook_path(self, playbook: str) -> str:
        """Resolve playbook path.

        Args:
            playbook: Playbook path or name

        Returns:
            Resolved playbook path
        """
        # If it's an absolute path, use it as is
        if os.path.isabs(playbook):
            return playbook
        
        # If it's a relative path, assume it's relative to playbook_dir
        return os.path.join(self.playbook_dir, playbook)

    def get_playbook_info(self, playbook: str) -> Dict[str, Any]:
        """Get information about a playbook.

        Args:
            playbook: Path to the playbook file

        Returns:
            Playbook information
        """
        try:
            playbook_path = self._resolve_playbook_path(playbook)
            
            if not os.path.exists(playbook_path):
                return {"error": "Playbook not found"}
            
            stat_info = os.stat(playbook_path)
            
            return {
                "path": playbook_path,
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
                "exists": True
            }
            
        except Exception as e:
            logger.error(f"Failed to get playbook info: {e}")
            return {"error": str(e)}

    def delete_playbook(self, playbook: str) -> bool:
        """Delete a playbook file.

        Args:
            playbook: Path to the playbook file

        Returns:
            True if deletion was successful
        """
        try:
            playbook_path = self._resolve_playbook_path(playbook)
            
            if os.path.exists(playbook_path):
                os.remove(playbook_path)
                logger.info(f"Deleted playbook: {playbook_path}")
                return True
            else:
                logger.warning(f"Playbook not found: {playbook_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete playbook: {e}")
            return False 