"""Parser for package metadata files."""

import yaml
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

from jsonschema import validate, ValidationError
from .package_schema import PACKAGE_SCHEMA, STEP_SCHEMA, PACKAGE_INFO_SCHEMA
from core.exceptions import MetadataError, ValidationError as CustomValidationError


logger = logging.getLogger(__name__)


class MetadataParser:
    """Parser for package metadata files."""

    def __init__(self):
        """Initialize metadata parser."""
        pass

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a metadata file.

        Args:
            file_path: Path to the metadata file

        Returns:
            Parsed metadata

        Raises:
            MetadataError: If parsing fails
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise MetadataError(f"Metadata file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as YAML first
            try:
                metadata = yaml.safe_load(content)
            except yaml.YAMLError as e:
                # Try to parse as JSON
                try:
                    metadata = json.loads(content)
                except json.JSONDecodeError as json_e:
                    raise MetadataError(f"Failed to parse metadata file: {e} or {json_e}")
            
            # Validate the metadata
            self.validate_metadata(metadata)
            
            return metadata
            
        except Exception as e:
            if isinstance(e, MetadataError):
                raise
            logger.error(f"Failed to parse metadata file: {e}")
            raise MetadataError(f"Failed to parse metadata file: {e}")

    def parse_string(self, content: str) -> Dict[str, Any]:
        """Parse metadata from a string.

        Args:
            content: Metadata content as string

        Returns:
            Parsed metadata

        Raises:
            MetadataError: If parsing fails
        """
        try:
            # Try to parse as YAML first
            try:
                metadata = yaml.safe_load(content)
            except yaml.YAMLError as e:
                # Try to parse as JSON
                try:
                    metadata = json.loads(content)
                except json.JSONDecodeError as json_e:
                    raise MetadataError(f"Failed to parse metadata content: {e} or {json_e}")
            
            # Validate the metadata
            self.validate_metadata(metadata)
            
            return metadata
            
        except Exception as e:
            if isinstance(e, MetadataError):
                raise
            logger.error(f"Failed to parse metadata content: {e}")
            raise MetadataError(f"Failed to parse metadata content: {e}")

    def validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata against schema.

        Args:
            metadata: Metadata to validate

        Raises:
            ValidationError: If validation fails
        """
        try:
            validate(instance=metadata, schema=PACKAGE_SCHEMA)
        except ValidationError as e:
            logger.error(f"Metadata validation failed: {e}")
            raise CustomValidationError(f"Metadata validation failed: {e}")

    def validate_step(self, step: Dict[str, Any]) -> None:
        """Validate a single step.

        Args:
            step: Step to validate

        Raises:
            ValidationError: If validation fails
        """
        try:
            validate(instance=step, schema=STEP_SCHEMA)
        except ValidationError as e:
            logger.error(f"Step validation failed: {e}")
            raise CustomValidationError(f"Step validation failed: {e}")

    def validate_package_info(self, package_info: Dict[str, Any]) -> None:
        """Validate package information.

        Args:
            package_info: Package info to validate

        Raises:
            ValidationError: If validation fails
        """
        try:
            validate(instance=package_info, schema=PACKAGE_INFO_SCHEMA)
        except ValidationError as e:
            logger.error(f"Package info validation failed: {e}")
            raise CustomValidationError(f"Package info validation failed: {e}")

    def get_package_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract package information from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            Package information
        """
        package_info = metadata.get("package", {})
        self.validate_package_info(package_info)
        return package_info

    def get_install_steps(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract installation steps from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            List of installation steps
        """
        steps = metadata.get("install_steps", [])
        
        # Validate each step
        for step in steps:
            self.validate_step(step)
        
        return steps

    def get_pre_install_steps(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract pre-installation steps from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            List of pre-installation steps
        """
        return metadata.get("pre_install", [])

    def get_post_install_steps(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract post-installation steps from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            List of post-installation steps
        """
        return metadata.get("post_install", [])

    def get_dependencies(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract dependencies from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            List of dependencies
        """
        return metadata.get("dependencies", [])

    def get_conflicts(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract conflicts from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            List of conflicts
        """
        return metadata.get("conflicts", [])

    def get_requirements(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract system requirements from metadata.

        Args:
            metadata: Parsed metadata

        Returns:
            System requirements
        """
        return metadata.get("requirements", {})

    def create_metadata_template(self, package_name: str, version: str) -> Dict[str, Any]:
        """Create a metadata template.

        Args:
            package_name: Package name
            version: Package version

        Returns:
            Metadata template
        """
        template = {
            "package": {
                "name": package_name,
                "version": version,
                "description": "Package description",
                "author": "Package author",
                "license": "Package license"
            },
            "install_steps": [
                {
                    "type": "apt_package",
                    "action": "install",
                    "packages": ["example-package"],
                    "rollback": "auto",
                    "description": "Install example package"
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
                "architectures": ["amd64", "arm64"]
            }
        }
        
        return template

    def save_metadata(self, metadata: Dict[str, Any], file_path: str) -> None:
        """Save metadata to a file.

        Args:
            metadata: Metadata to save
            file_path: Path to save the metadata

        Raises:
            MetadataError: If saving fails
        """
        try:
            # Validate metadata before saving
            self.validate_metadata(metadata)
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata, f, default_flow_style=False, indent=2)
            
            logger.info(f"Metadata saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise MetadataError(f"Failed to save metadata: {e}")

    def merge_metadata(self, base_metadata: Dict[str, Any], 
                      override_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two metadata dictionaries.

        Args:
            base_metadata: Base metadata
            override_metadata: Metadata to override with

        Returns:
            Merged metadata
        """
        import copy
        
        # Deep copy the base metadata
        merged = copy.deepcopy(base_metadata)
        
        # Merge package info
        if "package" in override_metadata:
            merged["package"].update(override_metadata["package"])
        
        # Merge install steps (append)
        if "install_steps" in override_metadata:
            merged["install_steps"].extend(override_metadata["install_steps"])
        
        # Merge pre-install steps (append)
        if "pre_install" in override_metadata:
            merged["pre_install"].extend(override_metadata["pre_install"])
        
        # Merge post-install steps (append)
        if "post_install" in override_metadata:
            merged["post_install"].extend(override_metadata["post_install"])
        
        # Merge dependencies (append)
        if "dependencies" in override_metadata:
            merged["dependencies"].extend(override_metadata["dependencies"])
        
        # Merge conflicts (append)
        if "conflicts" in override_metadata:
            merged["conflicts"].extend(override_metadata["conflicts"])
        
        # Merge requirements (update)
        if "requirements" in override_metadata:
            merged["requirements"].update(override_metadata["requirements"])
        
        return merged 