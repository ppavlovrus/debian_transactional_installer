"""JSON Schema for package metadata validation."""

PACKAGE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["package", "install_steps"],
    "properties": {
        "package": {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_-]+$",
                    "description": "Package name (alphanumeric, underscore, hyphen only)"
                },
                "version": {
                    "type": "string",
                    "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(-[a-zA-Z0-9._]+)?$",
                    "description": "Package version in semantic versioning format"
                },
                "description": {
                    "type": "string",
                    "description": "Optional package description"
                },
                "author": {
                    "type": "string",
                    "description": "Package author"
                },
                "license": {
                    "type": "string",
                    "description": "Package license"
                }
            },
            "additionalProperties": False
        },
        "install_steps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "apt_package",
                            "file_copy",
                            "systemd_service",
                            "user_management",
                            "ansible_playbook"
                        ],
                        "description": "Type of installation step"
                    },
                    "rollback": {
                        "type": "string",
                        "enum": ["auto", "manual", "ansible"],
                        "default": "auto",
                        "description": "Rollback strategy for this step"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional step description"
                    }
                },
                "allOf": [
                    {
                        "if": {
                            "properties": {"type": {"const": "apt_package"}}
                        },
                        "then": {
                            "required": ["action", "packages"],
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["install", "remove", "update"],
                                    "description": "APT action to perform"
                                },
                                "packages": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "string",
                                        "pattern": "^[a-zA-Z0-9._+-]+$"
                                    },
                                    "description": "List of package names"
                                },
                                "update_cache": {
                                    "type": "boolean",
                                    "default": True,
                                    "description": "Whether to update package cache before installation"
                                }
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {"type": {"const": "file_copy"}}
                        },
                        "then": {
                            "required": ["src", "dest"],
                            "properties": {
                                "src": {
                                    "type": "string",
                                    "description": "Source file path"
                                },
                                "dest": {
                                    "type": "string",
                                    "description": "Destination file path"
                                },
                                "owner": {
                                    "type": "string",
                                    "description": "File owner (username)"
                                },
                                "group": {
                                    "type": "string",
                                    "description": "File group"
                                },
                                "mode": {
                                    "type": "string",
                                    "pattern": "^[0-7]{3,4}$",
                                    "description": "File permissions in octal format"
                                }
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {"type": {"const": "systemd_service"}}
                        },
                        "then": {
                            "required": ["service", "action"],
                            "properties": {
                                "service": {
                                    "type": "string",
                                    "description": "Systemd service name"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["enable", "disable", "start", "stop", "restart"],
                                    "description": "Service action to perform"
                                }
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {"type": {"const": "user_management"}}
                        },
                        "then": {
                            "required": ["username", "action"],
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "pattern": "^[a-zA-Z_][a-zA-Z0-9_-]*$",
                                    "description": "Username"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["create", "remove", "modify"],
                                    "description": "User action to perform"
                                },
                                "user_data": {
                                    "type": "object",
                                    "properties": {
                                        "home": {
                                            "type": "string",
                                            "description": "Home directory path"
                                        },
                                        "shell": {
                                            "type": "string",
                                            "description": "Default shell"
                                        },
                                        "groups": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of groups"
                                        },
                                        "system": {
                                            "type": "boolean",
                                            "description": "Whether this is a system user"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    {
                        "if": {
                            "properties": {"type": {"const": "ansible_playbook"}}
                        },
                        "then": {
                            "required": ["playbook"],
                            "properties": {
                                "playbook": {
                                    "type": "string",
                                    "description": "Path to Ansible playbook file"
                                },
                                "rollback_playbook": {
                                    "type": "string",
                                    "description": "Path to rollback playbook file"
                                },
                                "vars": {
                                    "type": "object",
                                    "description": "Variables to pass to the playbook"
                                },
                                "inventory": {
                                    "type": "string",
                                    "description": "Path to inventory file or inventory string"
                                }
                            }
                        }
                    }
                ]
            }
        },
        "pre_install": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["script", "ansible_playbook"],
                        "description": "Type of pre-installation step"
                    },
                    "script": {
                        "type": "string",
                        "description": "Script to execute (for script type)"
                    },
                    "playbook": {
                        "type": "string",
                        "description": "Ansible playbook to execute (for ansible_playbook type)"
                    },
                    "vars": {
                        "type": "object",
                        "description": "Variables for Ansible playbook"
                    }
                }
            }
        },
        "post_install": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["script", "ansible_playbook"],
                        "description": "Type of post-installation step"
                    },
                    "script": {
                        "type": "string",
                        "description": "Script to execute (for script type)"
                    },
                    "playbook": {
                        "type": "string",
                        "description": "Ansible playbook to execute (for ansible_playbook type)"
                    },
                    "vars": {
                        "type": "object",
                        "description": "Variables for Ansible playbook"
                    }
                }
            }
        },
        "dependencies": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "List of package dependencies"
            }
        },
        "conflicts": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "List of conflicting packages"
            }
        },
        "requirements": {
            "type": "object",
            "properties": {
                "min_memory": {
                    "type": "integer",
                    "description": "Minimum memory requirement in MB"
                },
                "min_disk_space": {
                    "type": "integer",
                    "description": "Minimum disk space requirement in MB"
                },
                "os_version": {
                    "type": "string",
                    "description": "Minimum OS version requirement"
                },
                "architectures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Supported architectures"
                }
            }
        }
    },
    "additionalProperties": False
}

# Schema for individual step validation
STEP_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["type"],
    "properties": {
        "type": {
            "type": "string",
            "enum": [
                "apt_package",
                "file_copy",
                "systemd_service",
                "user_management",
                "ansible_playbook"
            ]
        }
    }
}

# Schema for package info validation
PACKAGE_INFO_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "version"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9_-]+$"
        },
        "version": {
            "type": "string",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(-[a-zA-Z0-9._]+)?$"
        },
        "description": {"type": "string"},
        "author": {"type": "string"},
        "license": {"type": "string"}
    },
    "additionalProperties": False
} 