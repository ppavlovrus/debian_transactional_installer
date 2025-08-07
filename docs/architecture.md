# Architecture Documentation

## Overview

The Debian Transactional Installer is designed as a modular, transaction-based system for atomic package installations on Debian-like systems. It ensures that either all installation steps complete successfully, or the system is rolled back to its previous state.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface                            │
│  (cli/main.py)                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Transaction Manager                          │
│  (core/transaction_manager.py)                             │
│  • Orchestrates installation process                        │
│  • Manages transaction lifecycle                            │
│  • Handles rollback on failures                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Core Components                              │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │  State Tracker  │ Rollback Engine │  Step Executor  │   │
│  │  (core/state_   │ (core/rollback_ │ (backends/step_ │   │
│  │   tracker.py)   │  engine.py)     │  executor.py)   │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Storage Layer                                │
│  (storage/transaction_db.py)                                │
│  • SQLite database for transaction state                    │
│  • WAL mode for ACID compliance                             │
│  • Snapshot storage for rollback                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Backend Handlers                             │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │ Simple Handlers │ Ansible Backend │ Metadata Parser │   │
│  │ (backends/      │ (backends/      │ (metadata/      │   │
│  │  simple_        │  ansible_       │  metadata_      │   │
│  │  handlers.py)   │  backend.py)    │  parser.py)     │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Transaction Manager (`core/transaction_manager.py`)

The central orchestrator that manages the entire installation process.

**Key Responsibilities:**
- Begin, commit, and rollback transactions
- Execute installation steps in order
- Handle failures and trigger rollbacks
- Maintain transaction state

**Key Methods:**
```python
class TransactionManager:
    def begin_transaction(self, package_name: str, metadata: Dict[str, Any]) -> int
    def execute_steps(self, steps: List[Dict[str, Any]]) -> None
    def commit_transaction(self) -> None
    def rollback_transaction(self) -> None
    def get_transaction_status(self, transaction_id: int) -> Dict[str, Any]
```

**Transaction Lifecycle:**
1. **Begin**: Create transaction record, validate metadata
2. **Execute**: Run each step with snapshot creation
3. **Commit**: Mark transaction as successful, cleanup snapshots
4. **Rollback**: Restore system state on failure

### 2. State Tracker (`core/state_tracker.py`)

Manages system state snapshots for rollback operations.

**Key Responsibilities:**
- Create snapshots before each step
- Store file states, package lists, service states
- Provide rollback data to RollbackEngine

**Snapshot Types:**
- **File Snapshots**: File existence, permissions, content
- **Package Snapshots**: Installed package lists
- **Service Snapshots**: Systemd service states
- **User Snapshots**: User account information

### 3. Rollback Engine (`core/rollback_engine.py`)

Executes rollback operations to restore system state.

**Key Responsibilities:**
- Execute rollback steps in reverse order
- Handle different rollback strategies
- Restore files, packages, services, users

**Rollback Strategies:**
- **Auto**: Automatic rollback using snapshots
- **Manual**: Execute custom rollback scripts
- **Ansible**: Use Ansible playbooks for rollback

### 4. Step Executor (`backends/step_executor.py`)

Executes individual installation steps.

**Supported Step Types:**
- `apt_package`: Install/remove/update packages
- `file_copy`: Copy files with permissions
- `custom_script`: Execute custom scripts
- `systemd_service`: Manage systemd services
- `user_management`: Create/modify users
- `ansible_playbook`: Execute Ansible playbooks

## Storage Architecture

### Database Schema

The system uses SQLite with WAL (Write-Ahead Logging) for ACID compliance.

**Tables:**

1. **transactions**
   ```sql
   CREATE TABLE transactions (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       package_name TEXT NOT NULL,
       metadata_hash TEXT NOT NULL,
       metadata TEXT NOT NULL,
       status TEXT DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **steps**
   ```sql
   CREATE TABLE steps (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       transaction_id INTEGER NOT NULL,
       step_order INTEGER NOT NULL,
       step_type TEXT NOT NULL,
       step_data TEXT NOT NULL,
       status TEXT DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (transaction_id) REFERENCES transactions (id)
   );
   ```

3. **snapshots**
   ```sql
   CREATE TABLE snapshots (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       transaction_id INTEGER NOT NULL,
       step_order INTEGER NOT NULL,
       snapshot_data TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (transaction_id) REFERENCES transactions (id)
   );
   ```

### Data Flow

```
1. Transaction Creation
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   CLI       │───▶│ Transaction │───▶│   SQLite    │
   │   Input     │    │   Manager   │    │   Database  │
   └─────────────┘    └─────────────┘    └─────────────┘

2. Step Execution
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Transaction │───▶│ State       │───▶│ Step        │───▶│ Backend     │
   │ Manager     │    │ Tracker     │    │ Executor    │    │ Handlers    │
   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                              │                   │
                              ▼                   ▼
                       ┌─────────────┐    ┌─────────────┐
                       │   SQLite    │    │   System    │
                       │ Snapshots   │    │ Operations  │
                       └─────────────┘    └─────────────┘

3. Rollback Process
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Transaction │───▶│ Rollback    │───▶│ State       │───▶│ System      │
   │ Manager     │    │ Engine      │    │ Restoration │    │ Restoration │
   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   SQLite    │
                       │ Snapshots   │
                       └─────────────┘
```

## Security Architecture

### 1. Privilege Management
- Root privileges required for system operations
- Privilege escalation only for specific operations
- Principle of least privilege

### 2. Input Validation
- JSON Schema validation for metadata
- Path traversal protection
- Command injection prevention

### 3. Isolation
- Docker container support
- Process isolation
- File system isolation

### 4. Audit Trail
- Comprehensive logging
- Transaction history
- Rollback tracking

## Error Handling

### Error Types

1. **ValidationError**: Invalid metadata or configuration
2. **TransactionError**: Transaction execution failures
3. **RollbackError**: Rollback operation failures
4. **SnapshotError**: State tracking failures

### Error Recovery

```
Error Detection
       │
       ▼
┌─────────────┐
│ Log Error   │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Create      │
│ Snapshot    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Execute     │
│ Rollback    │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Update      │
│ Status      │
└─────────────┘
```

## Performance Considerations

### 1. Database Performance
- WAL mode for concurrent access
- Indexed queries for transaction lookups
- Connection pooling for high concurrency

### 2. Snapshot Optimization
- Incremental snapshots
- Compression for large files
- Cleanup of old snapshots

### 3. Parallel Execution
- Independent steps can run in parallel
- Resource locking for shared resources
- Progress tracking for long operations

## Scalability

### 1. Horizontal Scaling
- Stateless transaction managers
- Shared database backend
- Load balancing for multiple instances

### 2. Vertical Scaling
- Connection pooling
- Memory optimization
- CPU utilization optimization

### 3. Storage Scaling
- Database sharding
- Distributed file storage
- Backup and recovery strategies

## Monitoring and Observability

### 1. Metrics
- Transaction success/failure rates
- Step execution times
- Rollback frequency
- Resource utilization

### 2. Logging
- Structured logging with correlation IDs
- Log levels for different environments
- Centralized log aggregation

### 3. Health Checks
- Database connectivity
- System resource availability
- Service health endpoints

## Deployment Architecture

### 1. Single Instance
```
┌─────────────────────────────────────────┐
│           Application Server            │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Transaction │  │   SQLite DB     │  │
│  │   Manager   │  │                 │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### 2. Docker Deployment
```
┌─────────────────────────────────────────┐
│           Docker Container              │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Transaction │  │   SQLite DB     │  │
│  │   Manager   │  │   (Volume)      │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### 3. Multi-Instance
```
┌─────────────────┐  ┌─────────────────┐
│   Instance 1    │  │   Instance 2    │
│ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │ Transaction │ │  │ │ Transaction │ │
│ │   Manager   │ │  │ │   Manager   │ │
│ └─────────────┘ │  │ └─────────────┘ │
└─────────────────┘  └─────────────────┘
         │                     │
         └─────────┬───────────┘
                   ▼
         ┌─────────────────┐
         │   Shared DB     │
         │   (PostgreSQL)  │
         └─────────────────┘
```

## Future Enhancements

### 1. Distributed Transactions
- Multi-node transaction coordination
- Consensus protocols
- Network partition handling

### 2. Advanced Rollback Strategies
- Time-based rollbacks
- Conditional rollbacks
- Partial rollbacks

### 3. Integration Capabilities
- Kubernetes operators
- CI/CD pipeline integration
- Configuration management tools

### 4. Performance Optimizations
- Caching layers
- Async operations
- Batch processing
