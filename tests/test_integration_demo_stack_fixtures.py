"""Integration test for demo stack using fixture files."""

import pytest
import tempfile
import os
import shutil
import yaml
from pathlib import Path
from unittest.mock import patch, Mock

from core.transaction_manager import TransactionManager
from core.exceptions import TransactionError


class TestDemoStackFixturesIntegration:
    """Integration test for demo stack using fixture files."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        
        # Path to fixture files
        self.fixture_dir = Path(__file__).parent / "fixtures" / "demo-stack"
        
        # Initialize transaction manager
        self.manager = TransactionManager(db_path=self.temp_db.name)
        
        # Load metadata from fixture file
        with open(self.fixture_dir / "metadata.yaml", "r") as f:
            self.demo_metadata = yaml.safe_load(f)

    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_fixture_files_exist(self):
        """Test that all fixture files exist and are accessible."""
        # Check metadata file
        assert (self.fixture_dir / "metadata.yaml").exists()
        
        # Check testsite directory
        testsite_dir = self.fixture_dir / "testsite"
        assert testsite_dir.exists()
        
        # Check individual files
        assert (testsite_dir / "index.html").exists()
        assert (testsite_dir / "nginx.conf").exists()
        assert (testsite_dir / "create_db.sh").exists()
        assert (testsite_dir / "delete_db.sh").exists()

    def test_fixture_metadata_structure(self):
        """Test that fixture metadata has correct structure."""
        assert "package" in self.demo_metadata
        assert "install_steps" in self.demo_metadata
        
        package = self.demo_metadata["package"]
        assert package["name"] == "demo-stack"
        assert package["version"] == "0.1"
        
        steps = self.demo_metadata["install_steps"]
        assert len(steps) == 4
        
        # Verify step types
        step_types = [step["type"] for step in steps]
        assert "apt_package" in step_types
        assert "file_copy" in step_types
        assert "custom_script" in step_types

    def test_fixture_file_contents(self):
        """Test that fixture files have correct content."""
        testsite_dir = self.fixture_dir / "testsite"
        
        # Test index.html content
        with open(testsite_dir / "index.html", "r") as f:
            content = f.read()
        
        assert "<title>Demo App</title>" in content
        assert "<h1>It works!</h1>" in content
        
        # Test nginx.conf content
        with open(testsite_dir / "nginx.conf", "r") as f:
            content = f.read()
        
        assert "listen 80" in content
        assert "root /var/www/testsite" in content
        assert "index index.html" in content
        
        # Test create_db.sh content
        with open(testsite_dir / "create_db.sh", "r") as f:
            content = f.read()
        
        assert "mkdir -p /var/www/testsite" in content
        assert "CREATE TABLE demo" in content
        
        # Test delete_db.sh content
        with open(testsite_dir / "delete_db.sh", "r") as f:
            content = f.read()
        
        assert "rm -f /var/www/testsite/site.db" in content

    def test_fixture_script_permissions(self):
        """Test that fixture scripts are executable."""
        testsite_dir = self.fixture_dir / "testsite"
        
        # Test create_db.sh is executable
        assert os.access(testsite_dir / "create_db.sh", os.X_OK)
        
        # Test delete_db.sh is executable
        assert os.access(testsite_dir / "delete_db.sh", os.X_OK)

    @patch('backends.step_executor.StepExecutor.execute_step')
    def test_demo_stack_installation_with_fixtures(self, mock_execute_step):
        """Test demo stack installation using fixture files."""
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
        
        # Check that steps were called with correct data
        calls = mock_execute_step.call_args_list
        
        # First step: apt_package
        assert calls[0][0][0]["type"] == "apt_package"
        assert calls[0][0][0]["packages"] == ["nginx"]
        assert calls[0][0][0]["rollback"] == "remove_packages"
        
        # Second step: file_copy (index.html)
        assert calls[1][0][0]["type"] == "file_copy"
        assert calls[1][0][0]["src"] == "./testsite/index.html"
        assert calls[1][0][0]["dest"] == "/var/www/testsite/index.html"
        assert calls[1][0][0]["rollback"] == "restore_original"
        
        # Third step: file_copy (nginx.conf)
        assert calls[2][0][0]["type"] == "file_copy"
        assert calls[2][0][0]["src"] == "./testsite/nginx.conf"
        assert calls[2][0][0]["dest"] == "/etc/nginx/sites-enabled/testsite.conf"
        assert calls[2][0][0]["rollback"] == "restore_original"
        
        # Fourth step: custom_script
        assert calls[3][0][0]["type"] == "custom_script"
        assert calls[3][0][0]["script"] == "create_db.sh"
        assert calls[3][0][0]["rollback_script"] == "delete_db.sh"
        
        # Commit transaction
        self.manager.commit_transaction()
        
        # Verify transaction status
        status = self.manager.get_transaction_status(transaction_id)
        assert status["status"] == "completed"

    def test_metadata_yaml_parsing(self):
        """Test that metadata.yaml can be parsed correctly."""
        # Test YAML parsing
        metadata_file = self.fixture_dir / "metadata.yaml"
        
        with open(metadata_file, "r") as f:
            parsed_metadata = yaml.safe_load(f)
        
        # Verify structure
        assert isinstance(parsed_metadata, dict)
        assert "package" in parsed_metadata
        assert "install_steps" in parsed_metadata
        
        # Verify package info
        package = parsed_metadata["package"]
        assert package["name"] == "demo-stack"
        assert package["version"] == "0.1"
        
        # Verify install steps
        steps = parsed_metadata["install_steps"]
        assert isinstance(steps, list)
        assert len(steps) == 4
        
        # Verify each step has required fields
        for step in steps:
            assert "type" in step
            assert step["type"] in ["apt_package", "file_copy", "custom_script"]

    def test_rollback_configurations(self):
        """Test that all steps have proper rollback configurations."""
        steps = self.demo_metadata["install_steps"]
        
        for step in steps:
            if step["type"] == "apt_package":
                assert "rollback" in step
                assert step["rollback"] == "remove_packages"
            elif step["type"] == "file_copy":
                assert "rollback" in step
                assert step["rollback"] == "restore_original"
            elif step["type"] == "custom_script":
                assert "rollback_script" in step
                assert step["rollback_script"] == "delete_db.sh" 