"""Integration test for demo stack installation."""

import pytest
import tempfile
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock

from core.transaction_manager import TransactionManager
from core.exceptions import TransactionError


class TestDemoStackIntegration:
    """Integration test for demo stack installation."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Create test files structure
        self.testsite_dir = os.path.join(self.temp_dir, "testsite")
        os.makedirs(self.testsite_dir, exist_ok=True)
        
        # Create test files
        self._create_test_files()
        
        # Initialize transaction manager
        self.manager = TransactionManager(db_path=self.temp_db.name)
        
        # Demo stack metadata
        self.demo_metadata = {
            "package": {
                "name": "demo-stack",
                "version": "0.1"
            },
            "install_steps": [
                {
                    "type": "apt_package",
                    "action": "install",
                    "packages": ["nginx"],
                    "rollback": "remove_packages"
                },
                {
                    "type": "file_copy",
                    "src": "./testsite/index.html",
                    "dest": "/var/www/testsite/index.html",
                    "rollback": "restore_original"
                },
                {
                    "type": "file_copy",
                    "src": "./testsite/nginx.conf",
                    "dest": "/etc/nginx/sites-enabled/testsite.conf",
                    "rollback": "restore_original"
                },
                {
                    "type": "custom_script",
                    "script": "create_db.sh",
                    "rollback_script": "delete_db.sh"
                }
            ]
        }

    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_files(self):
        """Create test files for the demo stack."""
        # Create index.html
        index_html = """<!DOCTYPE html>
<html>
<head><title>Demo App</title></head>
<body>
  <h1>It works!</h1>
</body>
</html>"""
        
        with open(os.path.join(self.testsite_dir, "index.html"), "w") as f:
            f.write(index_html)
        
        # Create nginx.conf
        nginx_conf = """server {
    listen 80;
    server_name _;
    root /var/www/testsite;
    index index.html;
}"""
        
        with open(os.path.join(self.testsite_dir, "nginx.conf"), "w") as f:
            f.write(nginx_conf)
        
        # Create create_db.sh
        create_db_script = """#!/bin/bash
mkdir -p /var/www/testsite
sqlite3 /var/www/testsite/site.db "CREATE TABLE demo(id INTEGER PRIMARY KEY, val TEXT);"
"""
        
        with open(os.path.join(self.testsite_dir, "create_db.sh"), "w") as f:
            f.write(create_db_script)
        
        # Make script executable
        os.chmod(os.path.join(self.testsite_dir, "create_db.sh"), 0o755)
        
        # Create delete_db.sh
        delete_db_script = """#!/bin/bash
rm -f /var/www/testsite/site.db
"""
        
        with open(os.path.join(self.testsite_dir, "delete_db.sh"), "w") as f:
            f.write(delete_db_script)
        
        # Make script executable
        os.chmod(os.path.join(self.testsite_dir, "delete_db.sh"), 0o755)

    @patch('backends.step_executor.StepExecutor.execute_step')
    def test_demo_stack_installation_success(self, mock_execute_step):
        """Test successful demo stack installation."""
        # Mock successful step execution
        mock_execute_step.return_value = {"success": True, "message": "Step completed"}
        
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="demo-stack",
            metadata=self.demo_metadata
        )
        
        assert transaction_id is not None
        
        # Execute all steps
        self.manager.execute_steps(self.demo_metadata["install_steps"])
        
        # Verify all steps were executed
        assert mock_execute_step.call_count == 4
        
        # Check that steps were called in correct order
        calls = mock_execute_step.call_args_list
        
        # First step: apt_package
        assert calls[0][0][0]["type"] == "apt_package"
        assert calls[0][0][0]["packages"] == ["nginx"]
        
        # Second step: file_copy (index.html)
        assert calls[1][0][0]["type"] == "file_copy"
        assert calls[1][0][0]["src"] == "./testsite/index.html"
        assert calls[1][0][0]["dest"] == "/var/www/testsite/index.html"
        
        # Third step: file_copy (nginx.conf)
        assert calls[2][0][0]["type"] == "file_copy"
        assert calls[2][0][0]["src"] == "./testsite/nginx.conf"
        assert calls[2][0][0]["dest"] == "/etc/nginx/sites-enabled/testsite.conf"
        
        # Fourth step: custom_script
        assert calls[3][0][0]["type"] == "custom_script"
        assert calls[3][0][0]["script"] == "create_db.sh"
        
        # Commit transaction
        self.manager.commit_transaction()
        
        # Verify transaction status
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "completed"

    @patch('backends.step_executor.StepExecutor.execute_step')
    def test_demo_stack_installation_failure_with_rollback(self, mock_execute_step):
        """Test demo stack installation failure with rollback."""
        # Mock step execution to fail on the third step
        def mock_step_execution(step):
            if step.get("type") == "file_copy" and "nginx.conf" in step.get("src", ""):
                raise Exception("Failed to copy nginx configuration")
            return {"success": True, "message": "Step completed"}
        
        mock_execute_step.side_effect = mock_step_execution
        
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="demo-stack",
            metadata=self.demo_metadata
        )
        
        # Execute steps (should fail on third step)
        with pytest.raises(TransactionError):
            self.manager.execute_steps(self.demo_metadata["install_steps"])
        
        # Verify only first two steps were executed
        assert mock_execute_step.call_count == 3
        
        # Check transaction status
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "rolled_back"

    @patch('backends.step_executor.StepExecutor.execute_step')
    @patch('core.rollback_engine.RollbackEngine.rollback_step')
    def test_demo_stack_rollback_execution(self, mock_rollback_step, mock_execute_step):
        """Test rollback execution for demo stack."""
        # Mock successful step execution
        mock_execute_step.return_value = {"success": True, "message": "Step completed"}
        mock_rollback_step.return_value = {"success": True, "message": "Rollback completed"}
        
        # Begin transaction
        transaction_id = self.manager.begin_transaction(
            package_name="demo-stack",
            metadata=self.demo_metadata
        )
        
        # Execute all steps
        self.manager.execute_steps(self.demo_metadata["install_steps"])
        
        # Rollback transaction
        self.manager.rollback_transaction()
        
        # Verify rollback was called for each step (in reverse order)
        assert mock_rollback_step.call_count == 4
        
        # Check rollback calls were made in reverse order
        calls = mock_rollback_step.call_args_list
        
        # Last step rolled back first: custom_script
        assert "custom_script" in str(calls[0])
        
        # Third step rolled back: file_copy (nginx.conf)
        assert "nginx.conf" in str(calls[1])
        
        # Second step rolled back: file_copy (index.html)
        assert "index.html" in str(calls[2])
        
        # First step rolled back: apt_package
        assert "apt_package" in str(calls[3])

    def test_demo_stack_metadata_validation(self):
        """Test demo stack metadata validation."""
        # Test valid metadata
        assert "package" in self.demo_metadata
        assert "install_steps" in self.demo_metadata
        assert self.demo_metadata["package"]["name"] == "demo-stack"
        assert self.demo_metadata["package"]["version"] == "0.1"
        assert len(self.demo_metadata["install_steps"]) == 4
        
        # Verify step types
        step_types = [step["type"] for step in self.demo_metadata["install_steps"]]
        assert "apt_package" in step_types
        assert "file_copy" in step_types
        assert "custom_script" in step_types
        
        # Verify rollback configurations
        for step in self.demo_metadata["install_steps"]:
            if step["type"] == "apt_package":
                assert step["rollback"] == "remove_packages"
            elif step["type"] == "file_copy":
                assert step["rollback"] == "restore_original"
            elif step["type"] == "custom_script":
                assert "rollback_script" in step

    def test_demo_stack_file_contents(self):
        """Test demo stack file contents are correct."""
        # Test index.html content
        index_path = os.path.join(self.testsite_dir, "index.html")
        with open(index_path, "r") as f:
            content = f.read()
        
        assert "<title>Demo App</title>" in content
        assert "<h1>It works!</h1>" in content
        
        # Test nginx.conf content
        nginx_path = os.path.join(self.testsite_dir, "nginx.conf")
        with open(nginx_path, "r") as f:
            content = f.read()
        
        assert "listen 80" in content
        assert "root /var/www/testsite" in content
        assert "index index.html" in content
        
        # Test create_db.sh content
        create_db_path = os.path.join(self.testsite_dir, "create_db.sh")
        with open(create_db_path, "r") as f:
            content = f.read()
        
        assert "mkdir -p /var/www/testsite" in content
        assert "CREATE TABLE demo" in content
        
        # Test delete_db.sh content
        delete_db_path = os.path.join(self.testsite_dir, "delete_db.sh")
        with open(delete_db_path, "r") as f:
            content = f.read()
        
        assert "rm -f /var/www/testsite/site.db" in content

    def test_demo_stack_script_permissions(self):
        """Test demo stack script permissions."""
        # Test create_db.sh is executable
        create_db_path = os.path.join(self.testsite_dir, "create_db.sh")
        assert os.access(create_db_path, os.X_OK)
        
        # Test delete_db.sh is executable
        delete_db_path = os.path.join(self.testsite_dir, "delete_db.sh")
        assert os.access(delete_db_path, os.X_OK) 