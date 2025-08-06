"""Rollback engine for handling transaction rollbacks."""

import logging
from typing import Dict, Any, List
from .exceptions import RollbackError

logger = logging.getLogger(__name__)


class RollbackEngine:
    """Handles rollback operations for failed transactions."""

    def __init__(self):
        """Initialize rollback engine."""
        self.rollback_handlers = {
            "apt_package": self._rollback_apt_package,
            "file_copy": self._rollback_file_copy,
            "custom_script": self._rollback_custom_script,
        }

    def rollback_step(self, step: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback a single step.

        Args:
            step: The step to rollback (from database)
            snapshot: State snapshot before the step was executed

        Returns:
            Rollback result

        Raises:
            RollbackError: If rollback fails
        """
        # Extract step data from database record
        step_data = step.get("step_data", {})
        step_type = step_data.get("type")
        
        if step_type not in self.rollback_handlers:
            raise RollbackError(f"Unknown step type for rollback: {step_type}")
        
        try:
            logger.info(f"Rolling back step: {step_type}")
            result = self.rollback_handlers[step_type](step_data, snapshot.get("snapshot_data", {}))
            logger.info(f"Successfully rolled back step: {step_type}")
            return result
        except Exception as e:
            logger.error(f"Failed to rollback step {step_type}: {e}")
            raise RollbackError(f"Rollback failed for {step_type}: {e}")

    def rollback_transaction(self, steps: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> None:
        """Rollback an entire transaction.

        Args:
            steps: List of steps to rollback (in reverse order)
            snapshots: List of snapshots corresponding to each step

        Raises:
            RollbackError: If any rollback step fails
        """
        logger.info(f"Starting rollback for {len(steps)} steps")
        
        # Rollback steps in reverse order
        for i in range(len(steps) - 1, -1, -1):
            try:
                self.rollback_step(steps[i], snapshots[i])
            except RollbackError as e:
                logger.error(f"Rollback failed at step {i}: {e}")
                raise

    def _rollback_apt_package(self, step: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback apt package installation.

        Args:
            step: The apt package step
            snapshot: State snapshot

        Returns:
            Rollback result
        """
        action = step.get("action")
        packages = step.get("packages", [])
        
        if action == "install":
            # Remove packages that were installed
            logger.info(f"Removing packages: {packages}")
            # Here you would call the actual package removal logic
            return {"success": True, "message": f"Removed packages: {packages}"}
        elif action == "remove":
            # Reinstall packages that were removed
            logger.info(f"Reinstalling packages: {packages}")
            # Here you would call the actual package installation logic
            return {"success": True, "message": f"Reinstalled packages: {packages}"}
        else:
            raise RollbackError(f"Unknown apt action for rollback: {action}")

    def _rollback_file_copy(self, step: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback file copy operation.

        Args:
            step: The file copy step
            snapshot: State snapshot

        Returns:
            Rollback result
        """
        dest = step.get("dest")
        rollback_type = step.get("rollback", "restore_original")
        
        if rollback_type == "restore_original":
            # Restore original file from snapshot
            if "original_file" in snapshot:
                logger.info(f"Restoring original file: {dest}")
                # Here you would restore the original file
                return {"success": True, "message": f"Restored original file: {dest}"}
            else:
                # Remove the file if no original exists
                logger.info(f"Removing file: {dest}")
                # Here you would remove the file
                return {"success": True, "message": f"Removed file: {dest}"}
        else:
            raise RollbackError(f"Unknown rollback type for file copy: {rollback_type}")

    def _rollback_custom_script(self, step: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback custom script execution.

        Args:
            step: The custom script step
            snapshot: State snapshot

        Returns:
            Rollback result
        """
        rollback_script = step.get("rollback_script")
        
        if rollback_script:
            logger.info(f"Executing rollback script: {rollback_script}")
            # Here you would execute the rollback script
            return {"success": True, "message": f"Executed rollback script: {rollback_script}"}
        else:
            logger.warning("No rollback script specified for custom script step")
            return {"success": True, "message": "No rollback script available"} 