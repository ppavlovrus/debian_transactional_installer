"""Tests for metadata parser."""

import pytest
import tempfile
import os
from pathlib import Path

from metadata.metadata_parser import MetadataParser
from core.exceptions import MetadataError, ValidationError


class TestMetadataParser:
    """Test cases for MetadataParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MetadataParser()
        
        self.valid_metadata = {
            "package": {
                "name": "test-package",
                "version": "1.0.0",
                "description": "Test package",
                "author": "Test Author",
                "license": "MIT"
            },
            "install_steps": [
                {
                    "type": "apt_package",
                    "action": "install",
                    "packages": ["nginx"],
                    "rollback": "auto",
                    "description": "Install nginx"
                }
            ],
            "pre_install": [],
            "post_install": [],
            "dependencies": [],
            "conflicts": [],
            "requirements": {
                "min_memory": 512,
                "min_disk_space": 100,
                "os_version": "11.0",
                "architectures": ["amd64"]
            }
        }

    def test_parse_valid_metadata(self):
        """Test parsing valid metadata."""
        metadata = self.parser.parse_string(self._metadata_to_yaml(self.valid_metadata))
        
        assert metadata["package"]["name"] == "test-package"
        assert metadata["package"]["version"] == "1.0.0"
        assert len(metadata["install_steps"]) == 1
        assert metadata["install_steps"][0]["type"] == "apt_package"

    def test_parse_invalid_metadata(self):
        """Test parsing invalid metadata."""
        invalid_metadata = {
            "package": {
                "name": "test-package"
                # Missing required 'version' field
            }
        }
        
        with pytest.raises(MetadataError):
            self.parser.parse_string(self._metadata_to_yaml(invalid_metadata))

    def test_parse_file(self):
        """Test parsing metadata from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(self._metadata_to_yaml(self.valid_metadata))
            temp_file = f.name
        
        try:
            metadata = self.parser.parse_file(temp_file)
            assert metadata["package"]["name"] == "test-package"
        finally:
            os.unlink(temp_file)

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file."""
        with pytest.raises(MetadataError):
            self.parser.parse_file("/nonexistent/file.yml")

    def test_get_package_info(self):
        """Test extracting package info."""
        package_info = self.parser.get_package_info(self.valid_metadata)
        
        assert package_info["name"] == "test-package"
        assert package_info["version"] == "1.0.0"
        assert package_info["description"] == "Test package"

    def test_get_install_steps(self):
        """Test extracting install steps."""
        steps = self.parser.get_install_steps(self.valid_metadata)
        
        assert len(steps) == 1
        assert steps[0]["type"] == "apt_package"
        assert steps[0]["action"] == "install"

    def test_validate_step(self):
        """Test step validation."""
        valid_step = {
            "type": "apt_package",
            "action": "install",
            "packages": ["nginx"]
        }
        
        # Should not raise exception
        self.parser.validate_step(valid_step)
        
        invalid_step = {
            "type": "invalid_type"
        }
        
        with pytest.raises(ValidationError):
            self.parser.validate_step(invalid_step)

    def test_create_metadata_template(self):
        """Test creating metadata template."""
        template = self.parser.create_metadata_template("test-package", "1.0.0")
        
        assert template["package"]["name"] == "test-package"
        assert template["package"]["version"] == "1.0.0"
        assert "install_steps" in template
        assert "requirements" in template

    def test_save_metadata(self):
        """Test saving metadata to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_metadata.yml")
            
            self.parser.save_metadata(self.valid_metadata, file_path)
            
            assert os.path.exists(file_path)
            
            # Verify saved content
            loaded_metadata = self.parser.parse_file(file_path)
            assert loaded_metadata["package"]["name"] == "test-package"

    def test_merge_metadata(self):
        """Test merging metadata."""
        base_metadata = {
            "package": {"name": "base", "version": "1.0.0"},
            "install_steps": [{"type": "apt_package", "action": "install", "packages": ["base"]}],
            "dependencies": ["base-dep"]
        }
        
        override_metadata = {
            "package": {"version": "2.0.0"},
            "install_steps": [{"type": "apt_package", "action": "install", "packages": ["override"]}],
            "dependencies": ["override-dep"]
        }
        
        merged = self.parser.merge_metadata(base_metadata, override_metadata)
        
        assert merged["package"]["name"] == "base"
        assert merged["package"]["version"] == "2.0.0"
        assert len(merged["install_steps"]) == 2
        assert len(merged["dependencies"]) == 2

    def _metadata_to_yaml(self, metadata):
        """Convert metadata dict to YAML string."""
        import yaml
        return yaml.dump(metadata, default_flow_style=False) 