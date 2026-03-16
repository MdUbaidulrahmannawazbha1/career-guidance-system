"""
Rate limiting configuration using ``slowapi``.

Endpoint-specific limits
------------------------
- ``POST /auth/login``      → 5 requests per minute
- ``POST /analyze/resume``  → 10 requests per hour
- ``GET|POST /predict/*``   → 20 requests per hour
- All other routes          → 100 requests per minute

Usage in ``app.main``
---------------------
::

    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    from app.middleware.rate_limiter import limiter

    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Then decorate individual routes::

    from app.middleware.rate_limiter import limiter

    @router.post("/login")
    @limiter.limit("5/minute")
    async def login(request: Request, ...):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Limiter singleton
# ---------------------------------------------------------------------------
# Uses the client's remote IP address as the rate-limit key.
# Override ``key_func`` with a user-aware callable if per-user limits
# are preferred (e.g. ``lambda req: req.state.current_user.id``).
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ---------------------------------------------------------------------------
# Per-route limit strings (import these in your router files)
# ---------------------------------------------------------------------------

#: Login endpoint: maximum 5 requests per minute per IP.
LIMIT_AUTH_LOGIN = "5/minute"

#: Resume analysis: maximum 10 requests per hour per IP.
LIMIT_ANALYZE_RESUME = "10/hour"

#: Career / placement prediction: maximum 20 requests per hour per IP.
LIMIT_PREDICT = "20/hour"

#: Default for all other routes (mirrors ``default_limits`` above).
LIMIT_DEFAULT = "100/minute"
