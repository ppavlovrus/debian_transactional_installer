"""Simple handlers for basic system operations."""

import os
import shutil
import subprocess
import logging
from typing import List, Dict, Any

from core.exceptions import StepExecutionError


logger = logging.getLogger(__name__)


class SimpleHandlers:
    """Handlers for simple system operations."""

    def install_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Install packages using apt.

        Args:
            packages: List of package names to install

        Returns:
            Installation result

        Raises:
            StepExecutionError: If installation fails
        """
        try:
            logger.info(f"Installing packages: {packages}")
            
            # Update package list first
            subprocess.run(["apt-get", "update"], check=True, capture_output=True)
            
            # Install packages
            result = subprocess.run(
                ["apt-get", "install", "-y"] + packages,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "packages": packages,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Package installation failed: {e}")
            raise StepExecutionError(f"Package installation failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during package installation: {e}")
            raise StepExecutionError(f"Package installation failed: {e}")

    def remove_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Remove packages using apt.

        Args:
            packages: List of package names to remove

        Returns:
            Removal result

        Raises:
            StepExecutionError: If removal fails
        """
        try:
            logger.info(f"Removing packages: {packages}")
            
            result = subprocess.run(
                ["apt-get", "remove", "-y"] + packages,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "packages": packages,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Package removal failed: {e}")
            raise StepExecutionError(f"Package removal failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during package removal: {e}")
            raise StepExecutionError(f"Package removal failed: {e}")

    def update_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Update packages using apt.

        Args:
            packages: List of package names to update

        Returns:
            Update result

        Raises:
            StepExecutionError: If update fails
        """
        try:
            logger.info(f"Updating packages: {packages}")
            
            # Update package list first
            subprocess.run(["apt-get", "update"], check=True, capture_output=True)
            
            # Update packages
            result = subprocess.run(
                ["apt-get", "upgrade", "-y"] + packages,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "packages": packages,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Package update failed: {e}")
            raise StepExecutionError(f"Package update failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during package update: {e}")
            raise StepExecutionError(f"Package update failed: {e}")

    def copy_file(self, src: str, dest: str) -> Dict[str, Any]:
        """Copy a file from source to destination.

        Args:
            src: Source file path
            dest: Destination file path

        Returns:
            Copy result

        Raises:
            StepExecutionError: If copy fails
        """
        try:
            logger.info(f"Copying file from {src} to {dest}")
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dest)
            
            return {
                "success": True,
                "src": src,
                "dest": dest
            }
            
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            raise StepExecutionError(f"File copy failed: {e}")

    def remove_file(self, file_path: str) -> Dict[str, Any]:
        """Remove a file.

        Args:
            file_path: Path to file to remove

        Returns:
            Removal result

        Raises:
            StepExecutionError: If removal fails
        """
        try:
            logger.info(f"Removing file: {file_path}")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "file_path": file_path,
                    "removed": True
                }
            else:
                return {
                    "success": True,
                    "file_path": file_path,
                    "removed": False,
                    "message": "File does not exist"
                }
            
        except Exception as e:
            logger.error(f"File removal failed: {e}")
            raise StepExecutionError(f"File removal failed: {e}")

    def enable_service(self, service_name: str) -> Dict[str, Any]:
        """Enable a systemd service.

        Args:
            service_name: Name of the service to enable

        Returns:
            Enable result

        Raises:
            StepExecutionError: If enable fails
        """
        try:
            logger.info(f"Enabling service: {service_name}")
            
            result = subprocess.run(
                ["systemctl", "enable", service_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "service": service_name,
                "action": "enable",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service enable failed: {e}")
            raise StepExecutionError(f"Service enable failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during service enable: {e}")
            raise StepExecutionError(f"Service enable failed: {e}")

    def disable_service(self, service_name: str) -> Dict[str, Any]:
        """Disable a systemd service.

        Args:
            service_name: Name of the service to disable

        Returns:
            Disable result

        Raises:
            StepExecutionError: If disable fails
        """
        try:
            logger.info(f"Disabling service: {service_name}")
            
            result = subprocess.run(
                ["systemctl", "disable", service_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "service": service_name,
                "action": "disable",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service disable failed: {e}")
            raise StepExecutionError(f"Service disable failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during service disable: {e}")
            raise StepExecutionError(f"Service disable failed: {e}")

    def start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a systemd service.

        Args:
            service_name: Name of the service to start

        Returns:
            Start result

        Raises:
            StepExecutionError: If start fails
        """
        try:
            logger.info(f"Starting service: {service_name}")
            
            result = subprocess.run(
                ["systemctl", "start", service_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "service": service_name,
                "action": "start",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service start failed: {e}")
            raise StepExecutionError(f"Service start failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during service start: {e}")
            raise StepExecutionError(f"Service start failed: {e}")

    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a systemd service.

        Args:
            service_name: Name of the service to stop

        Returns:
            Stop result

        Raises:
            StepExecutionError: If stop fails
        """
        try:
            logger.info(f"Stopping service: {service_name}")
            
            result = subprocess.run(
                ["systemctl", "stop", service_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "service": service_name,
                "action": "stop",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service stop failed: {e}")
            raise StepExecutionError(f"Service stop failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during service stop: {e}")
            raise StepExecutionError(f"Service stop failed: {e}")

    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a systemd service.

        Args:
            service_name: Name of the service to restart

        Returns:
            Restart result

        Raises:
            StepExecutionError: If restart fails
        """
        try:
            logger.info(f"Restarting service: {service_name}")
            
            result = subprocess.run(
                ["systemctl", "restart", service_name],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "service": service_name,
                "action": "restart",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service restart failed: {e}")
            raise StepExecutionError(f"Service restart failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during service restart: {e}")
            raise StepExecutionError(f"Service restart failed: {e}")

    def create_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a system user.

        Args:
            username: Username to create
            user_data: User configuration data

        Returns:
            Creation result

        Raises:
            StepExecutionError: If creation fails
        """
        try:
            logger.info(f"Creating user: {username}")
            
            cmd = ["useradd"]
            
            # Add user options based on user_data
            if user_data.get("home"):
                cmd.extend(["-d", user_data["home"]])
            if user_data.get("shell"):
                cmd.extend(["-s", user_data["shell"]])
            if user_data.get("groups"):
                cmd.extend(["-G", ",".join(user_data["groups"])])
            if user_data.get("system"):
                cmd.append("-r")
            
            cmd.append(username)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            return {
                "success": True,
                "username": username,
                "action": "create",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"User creation failed: {e}")
            raise StepExecutionError(f"User creation failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            raise StepExecutionError(f"User creation failed: {e}")

    def remove_user(self, username: str) -> Dict[str, Any]:
        """Remove a system user.

        Args:
            username: Username to remove

        Returns:
            Removal result

        Raises:
            StepExecutionError: If removal fails
        """
        try:
            logger.info(f"Removing user: {username}")
            
            result = subprocess.run(
                ["userdel", "-r", username],
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "success": True,
                "username": username,
                "action": "remove",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"User removal failed: {e}")
            raise StepExecutionError(f"User removal failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during user removal: {e}")
            raise StepExecutionError(f"User removal failed: {e}")

    def modify_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Modify a system user.

        Args:
            username: Username to modify
            user_data: User modification data

        Returns:
            Modification result

        Raises:
            StepExecutionError: If modification fails
        """
        try:
            logger.info(f"Modifying user: {username}")
            
            cmd = ["usermod"]
            
            # Add user options based on user_data
            if user_data.get("home"):
                cmd.extend(["-d", user_data["home"]])
            if user_data.get("shell"):
                cmd.extend(["-s", user_data["shell"]])
            if user_data.get("groups"):
                cmd.extend(["-G", ",".join(user_data["groups"])])
            
            cmd.append(username)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            return {
                "success": True,
                "username": username,
                "action": "modify",
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"User modification failed: {e}")
            raise StepExecutionError(f"User modification failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error during user modification: {e}")
            raise StepExecutionError(f"User modification failed: {e}") 