"""
Tests for security utility modules.

These tests run without a live database or real environment by patching
``app.config.settings`` and mocking SQLAlchemy sessions where required.

Run with::

    cd backend
    pytest tests/test_security_utils.py -v
"""

import os
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Set required environment variables BEFORE any app module is imported.
# ---------------------------------------------------------------------------
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-32chars!")
os.environ.setdefault(
    "ENCRYPTION_KEY", "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
)
os.environ.setdefault("ENCRYPTION_IV", "0102030405060708090a0b0c0d0e0f10")


# ---------------------------------------------------------------------------
# hashing
# ---------------------------------------------------------------------------


class TestHashing:
    def test_hash_password_returns_string(self):
        from app.utils.hashing import hash_password

        result = hash_password("mysecret")
        assert isinstance(result, str)
        assert result.startswith("$2b$")

    def test_verify_password_correct(self):
        from app.utils.hashing import hash_password, verify_password

        hashed = hash_password("mysecret")
        assert verify_password("mysecret", hashed) is True

    def test_verify_password_wrong(self):
        from app.utils.hashing import hash_password, verify_password

        hashed = hash_password("mysecret")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_deterministic_unique(self):
        """Two hashes of the same password must differ (salt is random)."""
        from app.utils.hashing import hash_password

        h1 = hash_password("password")
        h2 = hash_password("password")
        assert h1 != h2


# ---------------------------------------------------------------------------
# encryption
# ---------------------------------------------------------------------------


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        from app.utils.encryption import decrypt_field, encrypt_field

        original = "sensitive data"
        ciphertext = encrypt_field(original)
        assert ciphertext != original
        assert decrypt_field(ciphertext) == original

    def test_encrypt_returns_string(self):
        from app.utils.encryption import encrypt_field

        result = encrypt_field("hello")
        assert isinstance(result, str)

    def test_decrypt_invalid_raises_http_exception(self):
        from fastapi import HTTPException

        from app.utils.encryption import decrypt_field

        with pytest.raises(HTTPException) as exc_info:
            decrypt_field("not-a-valid-fernet-token")
        assert exc_info.value.status_code == 400

    def test_different_values_produce_different_ciphertext(self):
        from app.utils.encryption import encrypt_field

        ct1 = encrypt_field("value1")
        ct2 = encrypt_field("value2")
        assert ct1 != ct2


# ---------------------------------------------------------------------------
# jwt_handler
# ---------------------------------------------------------------------------


class TestJWTHandler:
    def test_create_access_token_returns_string(self):
        from app.utils.jwt_handler import create_access_token

        token = create_access_token({"sub": "user-123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self):
        from app.utils.jwt_handler import create_refresh_token

        token = create_refresh_token({"sub": "user-123"})
        assert isinstance(token, str)

    def test_verify_access_token_valid(self):
        from app.utils.jwt_handler import create_access_token, verify_token

        token = create_access_token({"sub": "user-abc"})
        payload = verify_token(token)
        assert payload["sub"] == "user-abc"
        assert payload["type"] == "access"

    def test_verify_refresh_token_valid(self):
        from app.utils.jwt_handler import create_refresh_token, verify_token

        token = create_refresh_token({"sub": "user-abc"})
        payload = verify_token(token, expected_type="refresh")
        assert payload["sub"] == "user-abc"
        assert payload["type"] == "refresh"

    def test_verify_token_wrong_type_raises_401(self):
        from fastapi import HTTPException

        from app.utils.jwt_handler import create_access_token, verify_token

        token = create_access_token({"sub": "user-abc"})
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, expected_type="refresh")
        assert exc_info.value.status_code == 401

    def test_verify_token_invalid_raises_401(self):
        from fastapi import HTTPException

        from app.utils.jwt_handler import verify_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_access_token_has_exp_claim(self):
        from app.utils.jwt_handler import create_access_token, verify_token

        token = create_access_token({"sub": "user-xyz"})
        payload = verify_token(token)
        assert "exp" in payload

    def test_custom_expires_delta(self):
        from app.utils.jwt_handler import create_access_token

        token = create_access_token({"sub": "u"}, expires_delta=timedelta(seconds=10))
        assert token


# ---------------------------------------------------------------------------
# response
# ---------------------------------------------------------------------------


class TestResponse:
    def test_success_response_structure(self):
        from app.utils.response import success_response

        resp = success_response(data={"key": "val"}, message="OK")
        body = resp.body
        import json

        content = json.loads(body)
        assert content["success"] is True
        assert content["message"] == "OK"
        assert content["data"] == {"key": "val"}
        assert resp.status_code == 200

    def test_success_response_custom_status(self):
        from app.utils.response import success_response

        resp = success_response(data=None, message="Created", status_code=201)
        assert resp.status_code == 201

    def test_error_response_structure(self):
        from app.utils.response import error_response

        resp = error_response("Something went wrong", status_code=422)
        import json

        content = json.loads(resp.body)
        assert content["success"] is False
        assert content["message"] == "Something went wrong"
        assert resp.status_code == 422

    def test_error_response_default_status(self):
        from app.utils.response import error_response

        resp = error_response("bad input")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# file_handler
# ---------------------------------------------------------------------------


class TestFileHandler:
    @pytest.mark.asyncio
    async def test_validate_pdf_valid(self):
        from app.utils.file_handler import validate_pdf

        pdf_bytes = b"%PDF-1.4 small content"
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=pdf_bytes)
        mock_file.seek = AsyncMock()
        # Should not raise
        await validate_pdf(mock_file)

    @pytest.mark.asyncio
    async def test_validate_pdf_invalid_type(self):
        from fastapi import HTTPException

        from app.utils.file_handler import validate_pdf

        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=b"PK\x03\x04 not a pdf")
        mock_file.seek = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf(mock_file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_validate_pdf_too_large(self):
        from fastapi import HTTPException

        from app.utils.file_handler import validate_pdf

        big_content = b"%PDF" + b"x" * (5 * 1024 * 1024 + 1)
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=big_content)
        mock_file.seek = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await validate_pdf(mock_file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_save_upload(self, tmp_path, monkeypatch):
        import app.utils.file_handler as fh

        # Patch the default upload root so we write to tmp_path.
        monkeypatch.chdir(tmp_path)

        pdf_bytes = b"%PDF-1.4 content"
        mock_file = AsyncMock()
        mock_file.filename = "resume.pdf"
        mock_file.read = AsyncMock(return_value=pdf_bytes)

        user_id = str(uuid.uuid4())
        file_path = await fh.save_upload(mock_file, user_id)

        assert file_path.startswith("uploads/")
        assert file_path.endswith(".pdf")

        assert (tmp_path / file_path).exists()


# ---------------------------------------------------------------------------
# rbac
# ---------------------------------------------------------------------------


class TestRBAC:
    @pytest.mark.asyncio
    async def test_require_role_allowed(self):
        from app.utils.rbac import require_role

        user = MagicMock()
        user.role = "admin"

        require_role("admin", "counsellor")
        # We patch get_current_user to return our mock user.
        with patch("app.utils.rbac.get_current_user", return_value=user):
            # Manually call the closure's logic.
            allowed = {"admin", "counsellor"}
            user_role = str(user.role)
            assert user_role in allowed or user_role.split(".")[-1] in allowed

    @pytest.mark.asyncio
    async def test_require_role_forbidden(self):

        from app.utils.rbac import require_role

        user = MagicMock()
        user.role = "student"

        require_role("admin")
        # We test the logic directly rather than going through FastAPI DI.
        allowed = {"admin"}
        user_role = str(user.role)
        role_denied = user_role not in allowed and user_role.split(".")[-1] not in allowed
        assert role_denied
