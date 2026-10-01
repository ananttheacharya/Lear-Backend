"""Security headers middleware for the local FastAPI bridge.

The desktop API serves JSON, streaming responses, WebSockets, and a few HTML
surfaces used for demos/incidents. This ASGI middleware injects browser security
headers at the raw ``http.response.start`` event so normal JSON responses,
streaming responses, redirects, and handled error responses all receive the same
baseline protection.
"""
from __future__ import annotations

import os
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# Keep this compatible with the existing inline demo/admin pages while still
# blocking high-risk defaults. The value is overrideable for deployments that
# can move inline scripts/styles to external assets and tighten the policy.
DEFAULT_CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "connect-src 'self' http: https: ws: wss:; "
    "upgrade-insecure-requests"
)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": DEFAULT_CONTENT_SECURITY_POLICY,
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def security_headers() -> dict[str, str]:
    """Return the headers to apply.

    ``LEAR_CSP`` lets production deployments ship a stricter CSP without code
    changes. Other header values stay fixed because loosening them silently would
    defeat the purpose of this middleware.
    """
    headers = dict(SECURITY_HEADERS)
    csp_override = os.getenv("LEAR_CSP")
    if csp_override:
        headers["Content-Security-Policy"] = csp_override
    return headers


class SecurityHeadersMiddleware:
    """Inject standard browser security headers into every HTTP response.

    Implemented as plain ASGI rather than ``BaseHTTPMiddleware`` so streaming
    responses keep their streaming behavior and still receive headers.
    Existing route-specific values are preserved only when they intentionally
    set a stricter/specific policy before the middleware runs.
    """

    def __init__(self, app: ASGIApp, headers: dict[str, str] | None = None) -> None:
        self.app = app
        self._headers = headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                for name, value in (self._headers or security_headers()).items():
                    response_headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_security_headers)


def required_security_header_names() -> tuple[str, ...]:
    """Names used by tests and the curl validation script documentation."""
    return tuple(SECURITY_HEADERS.keys())
