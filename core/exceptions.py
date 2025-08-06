"""Custom exceptions for TransactionalInstaller."""


class TransactionalInstallerError(Exception):
    """Base exception for TransactionalInstaller."""

    pass


class TransactionError(TransactionalInstallerError):
    """Raised when transaction fails."""

    pass


class RollbackError(TransactionalInstallerError):
    """Raised when rollback fails."""

    pass


class MetadataError(TransactionalInstallerError):
    """Raised when metadata parsing fails."""

    pass


class ValidationError(TransactionalInstallerError):
    """Raised when validation fails."""

    pass


class StepExecutionError(TransactionalInstallerError):
    """Raised when step execution fails."""

    pass


class DatabaseError(TransactionalInstallerError):
    """Raised when database operations fail."""

    pass


class SnapshotError(TransactionalInstallerError):
    """Raised when snapshot operations fail."""

    pass 