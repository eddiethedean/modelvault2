"""ModelVault error hierarchy."""

from __future__ import annotations

from typing import Any


class ModelVaultError(Exception):
    """Base exception for all ModelVault errors."""

    def __init__(self, message: str = "", *, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ContractError(ModelVaultError):
    """Raised when a persistence contract is invalid."""


class RegistrationError(ModelVaultError):
    """Raised when model registration fails."""


class BackendError(ModelVaultError):
    """Raised when a backend operation fails."""


class StorageError(ModelVaultError):
    """Raised when a storage strategy operation fails."""


class PlanningError(ModelVaultError):
    """Raised when execution planning fails."""


class ValidationError(ModelVaultError):
    """Raised when model validation fails on read or write."""


class DriftError(ModelVaultError):
    """Raised when stored contract hash differs from current contract."""


class RecordNotFoundError(ModelVaultError):
    """Raised when a record is not found."""
