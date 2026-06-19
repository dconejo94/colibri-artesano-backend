"""Azure Blob Storage integration for product images.

Encapsulates all Azure-specific logic behind ``BlobStorageService`` so the rest
of the app deals only in plain URLs. The service is import-safe and constructs
the Azure client lazily, so the test suite (which leaves the Azure settings
blank) imports and runs without touching Azure.
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from azure.storage.blob import BlobSasPermissions, generate_blob_sas

logger = logging.getLogger(__name__)

# Allowed image content types mapped to their canonical file extension.
_CONTENT_TYPE_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class StorageNotConfiguredError(RuntimeError):
    """Raised when an Azure operation is attempted without configured settings."""


class InvalidImageError(ValueError):
    """Raised when a filename/content type is not an allowed image type."""


class BlobStorageService:
    def __init__(
        self,
        *,
        account_name: str,
        account_key: str,
        container: str,
        base_url: str,
        sas_expiry_minutes: int = 15,
    ):
        self.account_name = account_name
        self.account_key = account_key
        self.container = container
        self.base_url = base_url.rstrip("/")
        self.sas_expiry_minutes = sas_expiry_minutes

    @property
    def is_configured(self) -> bool:
        return bool(self.account_name and self.account_key)

    def _require_configured(self) -> None:
        if not self.is_configured:
            raise StorageNotConfiguredError("Azure Blob Storage is not configured")

    def _resolve_extension(self, filename: str, content_type: str) -> str:
        """Pick a safe extension, validating the image is an allowed type."""
        normalized_type = content_type.strip().lower()
        if normalized_type not in _CONTENT_TYPE_EXT:
            raise InvalidImageError(f"Unsupported content type: {content_type}")

        ext = PurePosixPath(filename).suffix.lower()
        if ext not in _ALLOWED_EXTENSIONS:
            # Fall back to the extension implied by the content type.
            ext = _CONTENT_TYPE_EXT[normalized_type]
        return ext

    def generate_upload_sas(
        self, product_id: UUID, filename: str, content_type: str
    ) -> tuple[str, str, datetime]:
        """Build a short-lived write SAS for a direct-to-blob upload.

        Returns ``(upload_url, blob_url, expires_at)`` where ``upload_url`` is
        the SAS-signed URL the client PUTs the bytes to, and ``blob_url`` is the
        clean permanent public URL stored on the ProductImage.
        """
        self._require_configured()

        ext = self._resolve_extension(filename, content_type)
        blob_name = f"{product_id}/{uuid4().hex}{ext}"
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.sas_expiry_minutes
        )

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(create=True, write=True),
            expiry=expires_at,
        )

        blob_url = f"{self.base_url}/{self.container}/{blob_name}"
        upload_url = f"{blob_url}?{sas_token}"
        return upload_url, blob_url, expires_at

    def delete_blob(self, blob_url: str) -> None:
        """Best-effort delete of the blob behind a stored public URL.

        Never raises: failures are logged so removing a DB row can't 500 just
        because the blob is already gone or Azure is unreachable.
        """
        if not self.is_configured:
            return

        prefix = f"{self.base_url}/{self.container}/"
        if not blob_url.startswith(prefix):
            # Not one of our blobs (e.g. legacy/seed picsum URL) — nothing to do.
            return
        blob_name = blob_url[len(prefix) :]

        try:
            from azure.storage.blob import BlobServiceClient

            client = BlobServiceClient(
                account_url=self.base_url, credential=self.account_key
            )
            client.get_blob_client(self.container, blob_name).delete_blob()
        except Exception as exc:  # pragma: no cover - best effort cleanup
            logger.warning("Failed to delete blob %s: %s", blob_name, exc)
