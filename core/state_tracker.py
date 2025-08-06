"""State tracker for creating and managing system snapshots."""

import os
import shutil
import stat
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess

from .exceptions import SnapshotError


logger = logging.getLogger(__name__)


class StateTracker:
    """Tracks system state and creates snapshots for rollback."""

    def __init__(self, snapshot_dir: str = None):
        """Initialize state tracker.

        Args:
            snapshot_dir: Directory to store snapshots (defaults to temp directory if not provided)
        """
        if snapshot_dir is None:
            import tempfile
            self.snapshot_dir = Path(tempfile.mkdtemp(prefix="transactional_installer_"))
        else:
            self.snapshot_dir = Path(snapshot_dir)
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create a snapshot of current system state based on step type.

        Args:
            step: Installation step that requires snapshot

        Returns:
            Snapshot data
        """
        step_type = step.get("type")
        
        if step_type == "file_copy":
            return self._create_file_snapshot(step)
        elif step_type == "apt_package":
            return self._create_package_snapshot(step)
        elif step_type == "systemd_service":
            return self._create_service_snapshot(step)
        elif step_type == "user_management":
            return self._create_user_snapshot(step)
        elif step_type == "ansible_playbook":
            return self._create_ansible_snapshot(step)
        else:
            logger.warning(f"Unknown step type: {step_type}, creating minimal snapshot")
            return {"type": "minimal", "timestamp": self._get_timestamp()}

    def _create_file_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot for file operations.

        Args:
            step: File operation step

        Returns:
            File snapshot data
        """
        dest_path = step.get("dest")
        if not dest_path:
            return {"type": "file", "error": "No destination path specified"}

        snapshot = {
            "type": "file",
            "path": dest_path,
            "timestamp": self._get_timestamp()
        }

        try:
            if os.path.exists(dest_path):
                # Get file info
                stat_info = os.stat(dest_path)
                snapshot.update({
                    "exists": True,
                    "size": stat_info.st_size,
                    "permissions": stat_info.st_mode,
                    "owner": stat_info.st_uid,
                    "group": stat_info.st_gid,
                    "modified": stat_info.st_mtime
                })
                
                # Create backup if file exists
                backup_path = self._create_file_backup(dest_path)
                if backup_path:
                    snapshot["backup_path"] = str(backup_path)
            else:
                snapshot["exists"] = False

        except Exception as e:
            logger.error(f"Failed to create file snapshot for {dest_path}: {e}")
            snapshot["error"] = str(e)

        return snapshot

    def _create_package_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot for package operations.

        Args:
            step: Package operation step

        Returns:
            Package snapshot data
        """
        packages = step.get("packages", [])
        action = step.get("action", "install")

        snapshot = {
            "type": "package",
            "action": action,
            "packages": packages,
            "timestamp": self._get_timestamp()
        }

        try:
            if action == "install":
                # Check which packages are already installed
                installed_packages = self._get_installed_packages(packages)
                snapshot["already_installed"] = installed_packages
            elif action == "remove":
                # Check which packages are actually installed
                installed_packages = self._get_installed_packages(packages)
                snapshot["to_remove"] = installed_packages

        except Exception as e:
            logger.error(f"Failed to create package snapshot: {e}")
            snapshot["error"] = str(e)

        return snapshot

    def _create_service_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot for systemd service operations.

        Args:
            step: Service operation step

        Returns:
            Service snapshot data
        """
        service_name = step.get("service")
        action = step.get("action", "enable")

        snapshot = {
            "type": "service",
            "service": service_name,
            "action": action,
            "timestamp": self._get_timestamp()
        }

        try:
            if service_name:
                # Check current service status
                status = self._get_service_status(service_name)
                snapshot["current_status"] = status

        except Exception as e:
            logger.error(f"Failed to create service snapshot for {service_name}: {e}")
            snapshot["error"] = str(e)

        return snapshot

    def _create_user_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot for user management operations.

        Args:
            step: User operation step

        Returns:
            User snapshot data
        """
        username = step.get("username")
        action = step.get("action", "create")

        snapshot = {
            "type": "user",
            "username": username,
            "action": action,
            "timestamp": self._get_timestamp()
        }

        try:
            if username:
                # Check if user exists
                user_exists = self._check_user_exists(username)
                snapshot["exists"] = user_exists

                if user_exists and action == "remove":
                    # Get user info for potential restoration
                    user_info = self._get_user_info(username)
                    snapshot["user_info"] = user_info

        except Exception as e:
            logger.error(f"Failed to create user snapshot for {username}: {e}")
            snapshot["error"] = str(e)

        return snapshot

    def _create_ansible_snapshot(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot for Ansible playbook operations.

        Args:
            step: Ansible operation step

        Returns:
            Ansible snapshot data
        """
        playbook = step.get("playbook")
        vars_data = step.get("vars", {})

        snapshot = {
            "type": "ansible",
            "playbook": playbook,
            "vars": vars_data,
            "timestamp": self._get_timestamp()
        }

        # For Ansible, we mainly track the playbook and variables
        # The actual state changes will be handled by the playbook itself
        return snapshot

    def _create_file_backup(self, file_path: str) -> Optional[Path]:
        """Create a backup of a file.

        Args:
            file_path: Path to the file to backup

        Returns:
            Path to backup file or None if failed
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None

            # Create backup filename
            backup_name = f"{source_path.name}.backup.{int(self._get_timestamp())}"
            backup_path = self.snapshot_dir / backup_name

            # Copy file
            shutil.copy2(source_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    def _get_installed_packages(self, packages: list) -> list:
        """Get list of packages that are already installed.

        Args:
            packages: List of package names to check

        Returns:
            List of installed packages
        """
        installed = []
        for package in packages:
            try:
                result = subprocess.run(
                    ["dpkg", "-s", package],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    installed.append(package)
            except Exception as e:
                logger.warning(f"Failed to check package {package}: {e}")

        return installed

    def _get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get current status of a systemd service.

        Args:
            service_name: Name of the service

        Returns:
            Service status information
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True,
                check=False
            )
            
            is_active = result.returncode == 0
            
            result = subprocess.run(
                ["systemctl", "is-enabled", service_name],
                capture_output=True,
                text=True,
                check=False
            )
            
            is_enabled = result.returncode == 0

            return {
                "active": is_active,
                "enabled": is_enabled
            }

        except Exception as e:
            logger.warning(f"Failed to get service status for {service_name}: {e}")
            return {"error": str(e)}

    def _check_user_exists(self, username: str) -> bool:
        """Check if a user exists.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        try:
            result = subprocess.run(
                ["id", username],
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_user_info(self, username: str) -> Dict[str, Any]:
        """Get information about a user.

        Args:
            username: Username to get info for

        Returns:
            User information
        """
        try:
            result = subprocess.run(
                ["id", username],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return {"id_output": result.stdout.strip()}
            else:
                return {"error": "User not found"}

        except Exception as e:
            return {"error": str(e)}

    def _get_timestamp(self) -> float:
        """Get current timestamp.

        Returns:
            Current timestamp
        """
        import time
        return time.time()

    def cleanup_snapshots(self, transaction_id: int) -> None:
        """Clean up snapshots for a completed transaction.

        Args:
            transaction_id: ID of the completed transaction
        """
        try:
            # This would be implemented to clean up snapshots
            # after successful transaction completion
            logger.info(f"Cleaning up snapshots for transaction {transaction_id}")
        except Exception as e:
            logger.warning(f"Failed to cleanup snapshots: {e}")

    def restore_from_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore system state from a snapshot.

        Args:
            snapshot: Snapshot data to restore from

        Returns:
            True if restoration was successful
        """
        try:
            snapshot_type = snapshot.get("type")
            
            if snapshot_type == "file":
                return self._restore_file_snapshot(snapshot)
            elif snapshot_type == "package":
                return self._restore_package_snapshot(snapshot)
            elif snapshot_type == "service":
                return self._restore_service_snapshot(snapshot)
            elif snapshot_type == "user":
                return self._restore_user_snapshot(snapshot)
            else:
                logger.warning(f"Unknown snapshot type: {snapshot_type}")
                return False

        except Exception as e:
            logger.error(f"Failed to restore from snapshot: {e}")
            return False

    def _restore_file_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore file from snapshot.

        Args:
            snapshot: File snapshot data

        Returns:
            True if restoration was successful
        """
        try:
            file_path = snapshot.get("path")
            backup_path = snapshot.get("backup_path")
            
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                logger.info(f"Restored file: {file_path}")
                return True
            elif not snapshot.get("exists", True):
                # File didn't exist before, remove it
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed file: {file_path}")
                return True
            else:
                logger.warning(f"No backup available for {file_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to restore file {file_path}: {e}")
            return False

    def _restore_package_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore package state from snapshot.

        Args:
            snapshot: Package snapshot data

        Returns:
            True if restoration was successful
        """
        # Package restoration would be handled by the rollback engine
        # This is a placeholder for future implementation
        return True

    def _restore_service_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore service state from snapshot.

        Args:
            snapshot: Service snapshot data

        Returns:
            True if restoration was successful
        """
        # Service restoration would be handled by the rollback engine
        # This is a placeholder for future implementation
        return True

    def _restore_user_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Restore user state from snapshot.

        Args:
            snapshot: User snapshot data

        Returns:
            True if restoration was successful
        """
        # User restoration would be handled by the rollback engine
        # This is a placeholder for future implementation
        return True 