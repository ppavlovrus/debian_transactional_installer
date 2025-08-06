"""Tests for transaction manager."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from core.transaction_manager import TransactionManager
from core.exceptions import TransactionError, RollbackError


class TestTransactionManager:
    """Test cases for TransactionManager."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        self.manager = TransactionManager(db_path=self.temp_db.name)
        
        self.test_metadata = {
            "package": {
                "name": "test-package",
                "version": "1.0.0"
            },
            "install_steps": [
                {
                    "type": "apt_package",
                    "action": "install",
                    "packages": ["nginx"]
                }
            ]
        }

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_begin_transaction(self):
        """Test beginning a transaction."""
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        assert transaction_id is not None
        assert self.manager.current_transaction_id == transaction_id

    def test_begin_transaction_without_metadata(self):
        """Test beginning a transaction with minimal metadata."""
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata={"package": {"name": "test", "version": "1.0.0"}}
        )
        
        assert transaction_id is not None

    @patch('core.transaction_manager.StepExecutor')
    def test_execute_steps_success(self, mock_step_executor):
        """Test successful step execution."""
        # Mock step executor
        mock_executor = Mock()
        mock_executor.execute_step.return_value = {"success": True}
        mock_step_executor.return_value = mock_executor
        
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        # Execute steps
        steps = [
            {
                "type": "apt_package",
                "action": "install",
                "packages": ["nginx"]
            }
        ]
        
        self.manager.execute_steps(steps)
        
        # Verify step was executed
        mock_executor.execute_step.assert_called_once()

    @patch('core.transaction_manager.StepExecutor')
    def test_execute_steps_failure(self, mock_step_executor):
        """Test step execution failure with rollback."""
        # Mock step executor to fail
        mock_executor = Mock()
        mock_executor.execute_step.side_effect = Exception("Step failed")
        mock_step_executor.return_value = mock_executor
        
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        # Execute steps (should fail and trigger rollback)
        steps = [
            {
                "type": "apt_package",
                "action": "install",
                "packages": ["nginx"]
            }
        ]
        
        with pytest.raises(TransactionError):
            self.manager.execute_steps(steps)

    def test_commit_transaction(self):
        """Test committing a transaction."""
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        # Commit transaction
        self.manager.commit_transaction()
        
        # Verify transaction is committed
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "completed"
        assert self.manager.current_transaction_id is None

    def test_commit_transaction_without_active(self):
        """Test committing without active transaction."""
        with pytest.raises(TransactionError):
            self.manager.commit_transaction()

    def test_rollback_transaction(self):
        """Test rolling back a transaction."""
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        # Rollback transaction
        self.manager.rollback_transaction()
        
        # Verify transaction is rolled back
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "rolled_back"
        assert self.manager.current_transaction_id is None

    def test_rollback_transaction_without_active(self):
        """Test rolling back without active transaction."""
        with pytest.raises(RollbackError):
            self.manager.rollback_transaction()

    def test_get_transaction_status(self):
        """Test getting transaction status."""
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        
        # Get status
        status = self.manager.get_transaction_status(transaction_id)
        
        assert status["id"] == transaction_id
        assert status["package_name"] == "test-package"
        assert status["status"] == "pending"

    def test_get_nonexistent_transaction_status(self):
        """Test getting status of nonexistent transaction."""
        with pytest.raises(Exception):
            self.manager.get_transaction_status(999)

    def test_list_transactions(self):
        """Test listing transactions."""
        # Create multiple transactions
        for i in range(3):
            self.manager.begin_transaction(
                package_name=f"package-{i}",
                metadata=self.test_metadata
            )
            self.manager.commit_transaction()
        
        # List transactions
        transactions = self.manager.list_transactions(limit=10)
        
        assert len(transactions) >= 3
        assert all("package_name" in tx for tx in transactions)

    def test_cleanup_old_transactions(self):
        """Test cleaning up old transactions."""
        # Create a transaction
        transaction_id = self.manager.begin_transaction(
            package_name="test-package",
            metadata=self.test_metadata
        )
        self.manager.commit_transaction()
        
        # Cleanup (should not remove recent transactions)
        count = self.manager.cleanup_old_transactions(days=1)
        
        # Verify transaction still exists
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "completed" 