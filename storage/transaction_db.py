"""Transaction database for storing transaction state."""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TransactionDB:
    """Database interface for transaction storage."""

    def __init__(self, db_path: str):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL,
                    metadata_hash TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    step_order INTEGER NOT NULL,
                    step_type TEXT NOT NULL,
                    step_data TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            
            # Create snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    step_order INTEGER NOT NULL,
                    snapshot_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            
            conn.commit()

    def create_transaction(self, package_name: str, metadata_hash: str, metadata: Dict[str, Any]) -> int:
        """Create a new transaction.

        Args:
            package_name: Name of the package
            metadata_hash: Hash of the metadata
            metadata: Package metadata

        Returns:
            Transaction ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (package_name, metadata_hash, metadata)
                VALUES (?, ?, ?)
            """, (package_name, metadata_hash, json.dumps(metadata)))
            
            conn.commit()
            return cursor.lastrowid

    def record_step(self, transaction_id: int, step_order: int, step_type: str, 
                   step_data: Dict[str, Any], status: str = "pending") -> int:
        """Record a step in the database.

        Args:
            transaction_id: Transaction ID
            step_order: Step order number
            step_type: Type of step
            step_data: Step data
            status: Step status

        Returns:
            Step ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO steps (transaction_id, step_order, step_type, step_data, status)
                VALUES (?, ?, ?, ?, ?)
            """, (transaction_id, step_order, step_type, json.dumps(step_data), status))
            
            conn.commit()
            return cursor.lastrowid

    def update_step_status(self, transaction_id: int, step_order: int, status: str):
        """Update step status.

        Args:
            transaction_id: Transaction ID
            step_order: Step order number
            status: New status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE steps SET status = ? 
                WHERE transaction_id = ? AND step_order = ?
            """, (status, transaction_id, step_order))
            
            conn.commit()

    def save_snapshot(self, transaction_id: int, step_order: int, snapshot: Dict[str, Any]):
        """Save a state snapshot.

        Args:
            transaction_id: Transaction ID
            step_order: Step order number
            snapshot: State snapshot data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO snapshots (transaction_id, step_order, snapshot_data)
                VALUES (?, ?, ?)
            """, (transaction_id, step_order, json.dumps(snapshot)))
            
            conn.commit()

    def update_transaction_status(self, transaction_id: int, status: str):
        """Update transaction status.

        Args:
            transaction_id: Transaction ID
            status: New status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, transaction_id))
            
            conn.commit()

    def commit_transaction(self, transaction_id: int):
        """Commit a transaction by updating its status to completed.

        Args:
            transaction_id: Transaction ID
        """
        self.update_transaction_status(transaction_id, "completed")

    def get_transaction_status(self, transaction_id: int) -> Dict[str, Any]:
        """Get transaction status information.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction status information
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return {"status": "not_found"}
        
        steps = self.get_transaction_steps(transaction_id)
        snapshots = self.get_transaction_snapshots(transaction_id)
        
        return {
            "id": transaction_id,
            "package_name": transaction["package_name"],
            "status": transaction["status"],
            "created_at": transaction["created_at"],
            "updated_at": transaction["updated_at"],
            "steps_count": len(steps),
            "snapshots_count": len(snapshots)
        }

    def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction data or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, package_name, metadata_hash, metadata, status, created_at, updated_at
                FROM transactions WHERE id = ?
            """, (transaction_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "package_name": row[1],
                    "metadata_hash": row[2],
                    "metadata": json.loads(row[3]),
                    "status": row[4],
                    "created_at": row[5],
                    "updated_at": row[6]
                }
            return None

    def get_transaction_steps(self, transaction_id: int) -> List[Dict[str, Any]]:
        """Get all steps for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of steps
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, step_order, step_type, step_data, status, created_at
                FROM steps WHERE transaction_id = ? ORDER BY step_order
            """, (transaction_id,))
            
            steps = []
            for row in cursor.fetchall():
                steps.append({
                    "id": row[0],
                    "step_order": row[1],
                    "step_type": row[2],
                    "step_data": json.loads(row[3]),
                    "status": row[4],
                    "created_at": row[5]
                })
            return steps

    def get_transaction_snapshots(self, transaction_id: int) -> List[Dict[str, Any]]:
        """Get all snapshots for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            List of snapshots
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, step_order, snapshot_data, created_at
                FROM snapshots WHERE transaction_id = ? ORDER BY step_order
            """, (transaction_id,))
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append({
                    "id": row[0],
                    "step_order": row[1],
                    "snapshot_data": json.loads(row[2]),
                    "created_at": row[3]
                })
            return snapshots

    def list_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent transactions.

        Args:
            limit: Maximum number of transactions to return

        Returns:
            List of transactions
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, package_name, status, created_at, updated_at
                FROM transactions ORDER BY created_at DESC LIMIT ?
            """, (limit,))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    "id": row[0],
                    "package_name": row[1],
                    "status": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                })
            return transactions

    def cleanup_old_transactions(self, days: int = 30) -> int:
        """Clean up old completed transactions.

        Args:
            days: Number of days to keep transactions

        Returns:
            Number of transactions deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM transactions 
                WHERE status IN ('completed', 'failed') 
                AND created_at < datetime('now', '-{} days')
            """.format(days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count 