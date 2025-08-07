# API Reference

## Core Modules

### Transaction Manager (`core.transaction_manager`)

The central orchestrator for managing installation transactions.

#### `TransactionManager`

**Constructor:**
```python
TransactionManager(db_path: str = "/var/lib/transactional-installer/transactions.db")
```

**Methods:**

##### `begin_transaction(package_name: str, metadata: Dict[str, Any]) -> int`
Begin a new transaction for package installation.

**Parameters:**
- `package_name`: Name of the package being installed
- `metadata`: Package metadata dictionary

**Returns:**
- `int`: Transaction ID

**Raises:**
- `TransactionError`: If transaction creation fails

**Example:**
```python
manager = TransactionManager()
transaction_id = manager.begin_transaction(
    package_name="my-app",
    metadata={"package": {"name": "my-app", "version": "1.0.0"}}
)
```

##### `execute_steps(steps: List[Dict[str, Any]]) -> None`
Execute installation steps within the current transaction.

**Parameters:**
- `steps`: List of step configurations

**Raises:**
- `TransactionError`: If any step fails

**Example:**
```python
steps = [
    {
        "type": "apt_package",
        "action": "install",
        "packages": ["nginx"]
    }
]
manager.execute_steps(steps)
```

##### `commit_transaction() -> None`
Commit the current transaction.

**Raises:**
- `TransactionError`: If no active transaction

**Example:**
```python
manager.commit_transaction()
```

##### `rollback_transaction() -> None`
Rollback the current transaction.

**Raises:**
- `RollbackError`: If rollback fails

**Example:**
```python
manager.rollback_transaction()
```

##### `get_transaction_status(transaction_id: int) -> Dict[str, Any]`
Get status information for a transaction.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:**
- `Dict[str, Any]`: Transaction status information

**Example:**
```python
status = manager.get_transaction_status(123)
print(f"Status: {status['status']}")
```

##### `list_transactions(limit: int = 50) -> List[Dict[str, Any]]`
List recent transactions.

**Parameters:**
- `limit`: Maximum number of transactions to return

**Returns:**
- `List[Dict[str, Any]]`: List of transaction information

**Example:**
```python
transactions = manager.list_transactions(limit=10)
for tx in transactions:
    print(f"ID: {tx['id']}, Status: {tx['status']}")
```

##### `cleanup_old_transactions(days: int = 30) -> int`
Clean up old completed transactions.

**Parameters:**
- `days`: Remove transactions older than this many days

**Returns:**
- `int`: Number of transactions removed

**Example:**
```python
removed = manager.cleanup_old_transactions(days=7)
print(f"Removed {removed} old transactions")
```

### State Tracker (`core.state_tracker`)

Manages system state snapshots for rollback operations.

#### `StateTracker`

**Constructor:**
```python
StateTracker(snapshot_dir: str = None)
```

**Methods:**

##### `create_snapshot(step: Dict[str, Any]) -> Dict[str, Any]`
Create a snapshot of current system state based on step type.

**Parameters:**
- `step`: Installation step that requires snapshot

**Returns:**
- `Dict[str, Any]`: Snapshot data

**Example:**
```python
tracker = StateTracker()
snapshot = tracker.create_snapshot({
    "type": "file_copy",
    "dest": "/etc/nginx/nginx.conf"
})
```

##### `cleanup_snapshots(transaction_id: int) -> None`
Clean up snapshots for a completed transaction.

**Parameters:**
- `transaction_id`: Transaction ID

**Example:**
```python
tracker.cleanup_snapshots(123)
```

##### `restore_from_snapshot(snapshot: Dict[str, Any]) -> bool`
Restore system state from a snapshot.

**Parameters:**
- `snapshot`: Snapshot data to restore from

**Returns:**
- `bool`: True if restoration was successful

**Example:**
```python
success = tracker.restore_from_snapshot(snapshot)
if not success:
    print("Failed to restore from snapshot")
```

### Rollback Engine (`core.rollback_engine`)

Executes rollback operations to restore system state.

#### `RollbackEngine`

**Constructor:**
```python
RollbackEngine()
```

**Methods:**

##### `rollback_step(step: Dict[str, Any], snapshot: Dict[str, Any]) -> Dict[str, Any]`
Rollback a single step.

**Parameters:**
- `step`: The step to rollback
- `snapshot`: State snapshot before the step was executed

**Returns:**
- `Dict[str, Any]`: Rollback result

**Raises:**
- `RollbackError`: If rollback fails

**Example:**
```python
engine = RollbackEngine()
result = engine.rollback_step(step, snapshot)
print(f"Rollback result: {result['message']}")
```

##### `rollback_transaction(steps: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> None`
Rollback an entire transaction.

**Parameters:**
- `steps`: List of steps to rollback (in reverse order)
- `snapshots`: List of snapshots corresponding to each step

**Raises:**
- `RollbackError`: If any rollback step fails

**Example:**
```python
engine.rollback_transaction(steps, snapshots)
```

## Backend Modules

### Step Executor (`backends.step_executor`)

Executes different types of installation steps.

#### `StepExecutor`

**Constructor:**
```python
StepExecutor()
```

**Methods:**

##### `execute_step(step: Dict[str, Any]) -> Dict[str, Any]`
Execute a single step.

**Parameters:**
- `step`: Step configuration

**Returns:**
- `Dict[str, Any]`: Execution result

**Raises:**
- `Exception`: If step execution fails

**Example:**
```python
executor = StepExecutor()
result = executor.execute_step({
    "type": "apt_package",
    "action": "install",
    "packages": ["nginx"]
})
```

### Ansible Backend (`backends.ansible_backend`)

Handles Ansible playbook execution.

#### `AnsibleBackend`

**Constructor:**
```python
AnsibleBackend()
```

**Methods:**

##### `execute_playbook(playbook_path: str, vars: Dict[str, Any] = None, inventory: str = None) -> Dict[str, Any]`
Execute an Ansible playbook.

**Parameters:**
- `playbook_path`: Path to the playbook file
- `vars`: Variables to pass to the playbook
- `inventory`: Inventory file or string

**Returns:**
- `Dict[str, Any]`: Execution result

**Example:**
```python
backend = AnsibleBackend()
result = backend.execute_playbook(
    playbook_path="setup.yml",
    vars={"app_name": "myapp"},
    inventory="localhost,"
)
```

### Simple Handlers (`backends.simple_handlers`)

Handles simple system operations.

#### `SimpleHandlers`

**Constructor:**
```python
SimpleHandlers()
```

**Methods:**

##### `install_packages(packages: List[str], update_cache: bool = True) -> Dict[str, Any]`
Install packages using APT.

**Parameters:**
- `packages`: List of package names
- `update_cache`: Whether to update package cache

**Returns:**
- `Dict[str, Any]`: Installation result

**Example:**
```python
handlers = SimpleHandlers()
result = handlers.install_packages(["nginx", "python3"])
```

##### `remove_packages(packages: List[str]) -> Dict[str, Any]`
Remove packages using APT.

**Parameters:**
- `packages`: List of package names

**Returns:**
- `Dict[str, Any]`: Removal result

**Example:**
```python
result = handlers.remove_packages(["nginx"])
```

##### `copy_file(src: str, dest: str, owner: str = None, group: str = None, mode: str = None) -> Dict[str, Any]`
Copy a file with optional ownership and permissions.

**Parameters:**
- `src`: Source file path
- `dest`: Destination file path
- `owner`: File owner
- `group`: File group
- `mode`: File permissions (octal)

**Returns:**
- `Dict[str, Any]`: Copy result

**Example:**
```python
result = handlers.copy_file(
    src="./config.conf",
    dest="/etc/app/config.conf",
    owner="root",
    group="root",
    mode="644"
)
```

##### `manage_service(service: str, action: str) -> Dict[str, Any]`
Manage systemd services.

**Parameters:**
- `service`: Service name
- `action`: Action to perform (enable, disable, start, stop, restart)

**Returns:**
- `Dict[str, Any]`: Service management result

**Example:**
```python
result = handlers.manage_service("nginx", "enable")
```

##### `create_user(username: str, user_data: Dict[str, Any]) -> Dict[str, Any]`
Create a system user.

**Parameters:**
- `username`: Username
- `user_data`: User configuration data

**Returns:**
- `Dict[str, Any]`: User creation result

**Example:**
```python
result = handlers.create_user("appuser", {
    "home": "/home/appuser",
    "shell": "/bin/bash",
    "groups": ["users"]
})
```

## Storage Modules

### Transaction Database (`storage.transaction_db`)

Database interface for transaction storage.

#### `TransactionDB`

**Constructor:**
```python
TransactionDB(db_path: str)
```

**Methods:**

##### `create_transaction(package_name: str, metadata_hash: str, metadata: Dict[str, Any]) -> int`
Create a new transaction.

**Parameters:**
- `package_name`: Name of the package
- `metadata_hash`: Hash of the metadata
- `metadata`: Package metadata

**Returns:**
- `int`: Transaction ID

**Example:**
```python
db = TransactionDB("/path/to/db.sqlite")
transaction_id = db.create_transaction(
    package_name="my-app",
    metadata_hash="abc123",
    metadata={"package": {"name": "my-app"}}
)
```

##### `record_step(transaction_id: int, step_order: int, step_type: str, step_data: Dict[str, Any], status: str = "pending") -> int`
Record a step in the database.

**Parameters:**
- `transaction_id`: Transaction ID
- `step_order`: Step order number
- `step_type`: Type of step
- `step_data`: Step data
- `status`: Step status

**Returns:**
- `int`: Step ID

**Example:**
```python
step_id = db.record_step(
    transaction_id=123,
    step_order=1,
    step_type="apt_package",
    step_data={"packages": ["nginx"]}
)
```

##### `update_step_status(transaction_id: int, step_order: int, status: str)`
Update step status.

**Parameters:**
- `transaction_id`: Transaction ID
- `step_order`: Step order number
- `status`: New status

**Example:**
```python
db.update_step_status(123, 1, "completed")
```

##### `save_snapshot(transaction_id: int, step_order: int, snapshot: Dict[str, Any])`
Save a state snapshot.

**Parameters:**
- `transaction_id`: Transaction ID
- `step_order`: Step order number
- `snapshot`: State snapshot data

**Example:**
```python
db.save_snapshot(123, 1, {"type": "file", "path": "/etc/nginx.conf"})
```

##### `get_transaction(transaction_id: int) -> Optional[Dict[str, Any]]`
Get transaction by ID.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:**
- `Optional[Dict[str, Any]]`: Transaction data or None

**Example:**
```python
transaction = db.get_transaction(123)
if transaction:
    print(f"Status: {transaction['status']}")
```

##### `get_transaction_steps(transaction_id: int) -> List[Dict[str, Any]]`
Get all steps for a transaction.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:**
- `List[Dict[str, Any]]`: List of steps

**Example:**
```python
steps = db.get_transaction_steps(123)
for step in steps:
    print(f"Step {step['step_order']}: {step['step_type']}")
```

##### `get_transaction_snapshots(transaction_id: int) -> List[Dict[str, Any]]`
Get all snapshots for a transaction.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:**
- `List[Dict[str, Any]]`: List of snapshots

**Example:**
```python
snapshots = db.get_transaction_snapshots(123)
for snapshot in snapshots:
    print(f"Snapshot for step {snapshot['step_order']}")
```

##### `update_transaction_status(transaction_id: int, status: str)`
Update transaction status.

**Parameters:**
- `transaction_id`: Transaction ID
- `status`: New status

**Example:**
```python
db.update_transaction_status(123, "completed")
```

##### `commit_transaction(transaction_id: int)`
Commit a transaction by updating its status to completed.

**Parameters:**
- `transaction_id`: Transaction ID

**Example:**
```python
db.commit_transaction(123)
```

##### `get_transaction_status(transaction_id: int) -> Dict[str, Any]`
Get transaction status information.

**Parameters:**
- `transaction_id`: Transaction ID

**Returns:**
- `Dict[str, Any]`: Transaction status information

**Example:**
```python
status = db.get_transaction_status(123)
print(f"Steps: {status['steps_count']}")
```

##### `list_transactions(limit: int = 50) -> List[Dict[str, Any]]`
List recent transactions.

**Parameters:**
- `limit`: Maximum number of transactions to return

**Returns:**
- `List[Dict[str, Any]]`: List of transactions

**Example:**
```python
transactions = db.list_transactions(limit=10)
for tx in transactions:
    print(f"ID: {tx['id']}, Package: {tx['package_name']}")
```

##### `cleanup_old_transactions(days: int = 30) -> int`
Clean up old completed transactions.

**Parameters:**
- `days`: Number of days to keep transactions

**Returns:**
- `int`: Number of transactions deleted

**Example:**
```python
deleted = db.cleanup_old_transactions(days=7)
print(f"Deleted {deleted} old transactions")
```

## Metadata Modules

### Metadata Parser (`metadata.metadata_parser`)

Parses and validates package metadata.

#### `MetadataParser`

**Constructor:**
```python
MetadataParser()
```

**Methods:**

##### `parse_file(file_path: str) -> Dict[str, Any]`
Parse metadata from a file.

**Parameters:**
- `file_path`: Path to the metadata file

**Returns:**
- `Dict[str, Any]`: Parsed metadata

**Raises:**
- `MetadataError`: If parsing fails

**Example:**
```python
parser = MetadataParser()
metadata = parser.parse_file("package.yml")
```

##### `parse_string(content: str) -> Dict[str, Any]`
Parse metadata from a string.

**Parameters:**
- `content`: Metadata content as string

**Returns:**
- `Dict[str, Any]`: Parsed metadata

**Raises:**
- `MetadataError`: If parsing fails

**Example:**
```python
content = """
package:
  name: my-app
  version: 1.0.0
"""
metadata = parser.parse_string(content)
```

##### `validate_metadata(metadata: Dict[str, Any]) -> bool`
Validate metadata against schema.

**Parameters:**
- `metadata`: Metadata to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValidationError`: If validation fails

**Example:**
```python
is_valid = parser.validate_metadata(metadata)
if not is_valid:
    print("Invalid metadata")
```

##### `get_package_info(metadata: Dict[str, Any]) -> Dict[str, Any]`
Extract package information from metadata.

**Parameters:**
- `metadata`: Package metadata

**Returns:**
- `Dict[str, Any]`: Package information

**Example:**
```python
package_info = parser.get_package_info(metadata)
print(f"Name: {package_info['name']}")
```

##### `get_install_steps(metadata: Dict[str, Any]) -> List[Dict[str, Any]]`
Extract installation steps from metadata.

**Parameters:**
- `metadata`: Package metadata

**Returns:**
- `List[Dict[str, Any]]`: List of installation steps

**Example:**
```python
steps = parser.get_install_steps(metadata)
for step in steps:
    print(f"Step type: {step['type']}")
```

##### `validate_step(step: Dict[str, Any]) -> bool`
Validate a single step.

**Parameters:**
- `step`: Step to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValidationError`: If validation fails

**Example:**
```python
is_valid = parser.validate_step(step)
```

##### `create_metadata_template(package_name: str, version: str) -> Dict[str, Any]`
Create a metadata template.

**Parameters:**
- `package_name`: Package name
- `version`: Package version

**Returns:**
- `Dict[str, Any]`: Metadata template

**Example:**
```python
template = parser.create_metadata_template("my-app", "1.0.0")
```

##### `save_metadata(metadata: Dict[str, Any], file_path: str)`
Save metadata to a file.

**Parameters:**
- `metadata`: Metadata to save
- `file_path`: Output file path

**Example:**
```python
parser.save_metadata(metadata, "output.yml")
```

##### `merge_metadata(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]`
Merge two metadata dictionaries.

**Parameters:**
- `base`: Base metadata
- `override`: Override metadata

**Returns:**
- `Dict[str, Any]`: Merged metadata

**Example:**
```python
merged = parser.merge_metadata(base_metadata, override_metadata)
```

## CLI Module

### Main CLI (`cli.main`)

Command-line interface for the transactional installer.

#### Available Commands

##### `install`
Install a package.

**Usage:**
```bash
transactional-installer install <package_file> [options]
```

**Options:**
- `--dry-run`: Validate without installing
- `--force`: Force installation even if validation fails
- `--verbose`: Enable verbose output

**Example:**
```bash
sudo transactional-installer install my-app.yml
sudo transactional-installer install my-app.yml --dry-run
```

##### `rollback`
Rollback a transaction.

**Usage:**
```bash
transactional-installer rollback <transaction_id>
```

**Example:**
```bash
sudo transactional-installer rollback 123
```

##### `list`
List transactions.

**Usage:**
```bash
transactional-installer list [options]
```

**Options:**
- `--limit`: Maximum number of transactions to show
- `--status`: Filter by status

**Example:**
```bash
transactional-installer list --limit 10
transactional-installer list --status failed
```

##### `status`
Show transaction status.

**Usage:**
```bash
transactional-installer status <transaction_id>
```

**Example:**
```bash
transactional-installer status 123
```

##### `cleanup`
Clean up old transactions.

**Usage:**
```bash
transactional-installer cleanup [options]
```

**Options:**
- `--older-than`: Remove transactions older than N days

**Example:**
```bash
transactional-installer cleanup --older-than 30
```

##### `create-template`
Create a metadata template.

**Usage:**
```bash
transactional-installer create-template <package_name> <version> [options]
```

**Options:**
- `-o, --output`: Output file path

**Example:**
```bash
transactional-installer create-template my-app 1.0.0 -o my-app.yml
```

##### `validate`
Validate metadata.

**Usage:**
```bash
transactional-installer validate <package_file>
```

**Example:**
```bash
transactional-installer validate my-app.yml
```

## Exceptions

### Core Exceptions (`core.exceptions`)

#### `TransactionError`
Raised when transaction operations fail.

**Example:**
```python
try:
    manager.begin_transaction("my-app", metadata)
except TransactionError as e:
    print(f"Transaction failed: {e}")
```

#### `RollbackError`
Raised when rollback operations fail.

**Example:**
```python
try:
    manager.rollback_transaction()
except RollbackError as e:
    print(f"Rollback failed: {e}")
```

#### `SnapshotError`
Raised when snapshot operations fail.

**Example:**
```python
try:
    tracker.create_snapshot(step)
except SnapshotError as e:
    print(f"Snapshot failed: {e}")
```

#### `MetadataError`
Raised when metadata parsing or validation fails.

**Example:**
```python
try:
    parser.parse_file("invalid.yml")
except MetadataError as e:
    print(f"Metadata error: {e}")
```

#### `ValidationError`
Raised when data validation fails.

**Example:**
```python
try:
    parser.validate_metadata(metadata)
except ValidationError as e:
    print(f"Validation failed: {e}")
```
