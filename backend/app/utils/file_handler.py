"""
File upload utilities.

Provides helpers for validating PDF uploads and persisting files to the
``uploads/`` directory with a structured path that prevents collisions.
"""

import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

# Maximum allowed PDF upload size (5 MB).
_MAX_PDF_SIZE_BYTES = 5 * 1024 * 1024

# Magic bytes that identify a PDF file.
_PDF_MAGIC = b"%PDF"


async def validate_pdf(file: UploadFile) -> None:
    """
    Validate that the uploaded file is a valid PDF under 5 MB.

    The function reads the file content into memory so it can be inspected
    and then seeks back to the beginning so the caller can read it again.

    Parameters
    ----------
    file:
        The ``UploadFile`` object received from a FastAPI route.

    Raises
    ------
    HTTPException (400)
        If the file is not a PDF (checked via magic bytes) or exceeds 5 MB.
    """
    content = await file.read()

    # Check magic bytes – PDF files always start with ``%PDF``.
    if not content.startswith(_PDF_MAGIC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type: only PDF files are accepted",
        )

    # Check file size.
    if len(content) > _MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large: maximum allowed size is 5 MB",
        )

    # Seek back to the start so that subsequent reads work correctly.
    await file.seek(0)


async def save_upload(file: UploadFile, user_id: str) -> str:
    """
    Persist an uploaded file to the ``uploads/<user_id>/`` directory.

    A UUID-based filename is generated to prevent path traversal and
    filename collision issues.

    Parameters
    ----------
    file:
        The ``UploadFile`` object (should have already passed
        :func:`validate_pdf`).
    user_id:
        The ID of the user who owns the upload.  Used to create a
        per-user subdirectory.

    Returns
    -------
    str
        The relative file path where the file was saved
        (e.g. ``uploads/abc123/550e8400-….pdf``).
    """
    # Determine the safe file extension from the original filename.
    original_name = file.filename or "upload"
    suffix = Path(original_name).suffix.lower() or ".pdf"

    # Build a per-user directory under the configured upload root.
    upload_root = Path("uploads") / str(user_id)
    upload_root.mkdir(parents=True, exist_ok=True)

    # Generate a random filename to prevent collisions and path traversal.
    filename = f"{uuid.uuid4()}{suffix}"
    dest = upload_root / filename

    content = await file.read()
    async with aiofiles.open(dest, "wb") as out_file:
        await out_file.write(content)

    # Return the relative path (portable across deployments).
    return str(dest)
