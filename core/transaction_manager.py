"""Transaction manager for handling atomic installations."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json

from .exceptions import TransactionError, RollbackError
from .state_tracker import StateTracker
from .rollback_engine import RollbackEngine
from storage.transaction_db import TransactionDB
from backends.step_executor import StepExecutor


logger = logging.getLogger(__name__)


class TransactionManager:
    """Manages transaction lifecycle for package installations."""

    def __init__(self, db_path: str = "/var/lib/transactional-installer/transactions.db"):
        """Initialize transaction manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db = TransactionDB(db_path)
        self.state_tracker = StateTracker()
        self.rollback_engine = RollbackEngine()
        self.step_executor = StepExecutor()
        self.current_transaction_id: Optional[int] = None

    def begin_transaction(self, package_name: str, metadata: Dict[str, Any]) -> int:
        """Begin a new transaction.

        Args:
            package_name: Name of the package being installed
            metadata: Package metadata

        Returns:
            Transaction ID
        """
        metadata_hash = hashlib.sha256(
            json.dumps(metadata, sort_keys=True).encode()
        ).hexdigest()
        
        transaction_id = self.db.create_transaction(
            package_name=package_name,
            metadata_hash=metadata_hash,
            metadata=metadata
        )
        
        self.current_transaction_id = transaction_id
        logger.info(f"Started transaction {transaction_id} for package {package_name}")
        
        return transaction_id

    def execute_steps(self, steps: List[Dict[str, Any]]) -> None:
        """Execute installation steps within a transaction.

        Args:
            steps: List of installation steps

        Raises:
            TransactionError: If any step fails
        """
        if not self.current_transaction_id:
            raise TransactionError("No active transaction")

        for step_order, step in enumerate(steps, 1):
            try:
                logger.info(f"Executing step {step_order}: {step.get('type', 'unknown')}")
                
                # Create snapshot before step execution
                snapshot = self.state_tracker.create_snapshot(step)
                self.db.save_snapshot(
                    self.current_transaction_id, 
                    step_order, 
                    snapshot
                )
                
                # Record step in database
                self.db.record_step(
                    transaction_id=self.current_transaction_id,
                    step_order=step_order,
                    step_type=step.get("type"),
                    step_data=step,
                    status="pending"
                )
                
                # Execute step
                result = self.step_executor.execute_step(step)
                
                # Update step status
                self.db.update_step_status(
                    self.current_transaction_id, 
                    step_order, 
                    "completed"
                )
                
                logger.info(f"Step {step_order} completed successfully")
                
            except Exception as e:
                logger.error(f"Step {step_order} failed: {e}")
                self.db.update_step_status(
                    self.current_transaction_id, 
                    step_order, 
                    "failed"
                )
                self.rollback_transaction()
                raise TransactionError(f"Step {step_order} failed: {e}")

    def commit_transaction(self) -> None:
        """Commit the current transaction.

        Raises:
            TransactionError: If no active transaction
        """
        if not self.current_transaction_id:
            raise TransactionError("No active transaction")

        try:
            self.db.commit_transaction(self.current_transaction_id)
            logger.info(f"Transaction {self.current_transaction_id} committed successfully")
            
            # Clean up snapshots
            self.state_tracker.cleanup_snapshots(self.current_transaction_id)
            
        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            raise TransactionError(f"Commit failed: {e}")
        finally:
            self.current_transaction_id = None

    def rollback_transaction(self) -> None:
        """Rollback the current transaction.

        Raises:
            RollbackError: If rollback fails
        """
        if not self.current_transaction_id:
            raise RollbackError("No active transaction")

        try:
            logger.info(f"Rolling back transaction {self.current_transaction_id}")
            
            # Get failed step and all previous steps
            steps = self.db.get_transaction_steps(self.current_transaction_id)
            snapshots = self.db.get_transaction_snapshots(self.current_transaction_id)
            
            # Execute rollback in reverse order
            self.rollback_engine.rollback_transaction(steps, snapshots)
            
            # Mark transaction as rolled back
            self.db.update_transaction_status(self.current_transaction_id, "rolled_back")
            
            logger.info(f"Transaction {self.current_transaction_id} rolled back successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise RollbackError(f"Rollback failed: {e}")
        finally:
            self.current_transaction_id = None

    def get_transaction_status(self, transaction_id: int) -> Dict[str, Any]:
        """Get status of a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction status information
        """
        return self.db.get_transaction_status(transaction_id)

    def list_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent transactions.

        Args:
            limit: Maximum number of transactions to return

        Returns:
            List of transaction information
        """
        return self.db.list_transactions(limit)

    def cleanup_old_transactions(self, days: int = 30) -> int:
        """Clean up old transactions.

        Args:
            days: Remove transactions older than this many days

        Returns:
            Number of transactions removed
        """
        return self.db.cleanup_old_transactions(days) 