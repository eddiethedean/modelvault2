"""ModelVault — model integrity layer for Pydantic models."""

from modelvault._version import __version__
from modelvault.decorators import model
from modelvault.errors import ModelVaultError
from modelvault.vault import Vault

__all__ = ["ModelVaultError", "Vault", "model", "__version__"]
