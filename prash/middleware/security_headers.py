"""Security headers middleware for the local FastAPI bridge.

The desktop API serves JSON, streaming responses, WebSockets, and a few HTML
surfaces used for demos/incidents. This ASGI middleware injects browser security
headers at the raw ``http.response.start`` event so normal JSON responses,
streaming responses, redirects, and handled error responses all receive the same
baseline protection.

Lear is local-first: the development server normally runs as plain HTTP on
localhost. Transport-upgrade controls (HSTS and ``upgrade-insecure-requests``)
are therefore intentionally enabled only when the request is already HTTPS (or a
TLS terminator tells us it was HTTPS) or when the deployment explicitly marks
itself production.
"""
from __future__ import annotations

import os
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

HSTS_VALUE = "max-age=31536000; includeSubDomains"

BASE_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# Keep this compatible with the existing inline demo/admin pages while still
# blocking high-risk defaults. The value is overrideable for deployments that
# can move inline scripts/styles to external assets and tighten the policy.
DEFAULT_LOCAL_CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self' data:; "
    "connect-src 'self' http: https: ws: wss:;"
)


def _is_production() -> bool:
    """Return True when the process is explicitly running as production.

    ``ENVIRONMENT`` is the primary knob because it was requested in review.
    ``LEAR_ENVIRONMENT`` and ``PRASH_ENVIRONMENT`` are accepted as aliases so
    packagers can avoid overloading a generic variable if needed.
    """
    for key in ("ENVIRONMENT", "LEAR_ENVIRONMENT", "PRASH_ENVIRONMENT"):
        if os.getenv(key, "").strip().lower() == "production":
            return True
    return False


def _scope_is_https(scope: Scope) -> bool:
    """Detect HTTPS from ASGI scope and common proxy forwarding headers."""
    if scope.get("scheme") == "https":
        return True
    headers = Headers(scope=scope)
    forwarded_proto = headers.get("x-forwarded-proto", "")
    if forwarded_proto.split(",", 1)[0].strip().lower() == "https":
        return True
    forwarded_ssl = headers.get("x-forwarded-ssl", "").strip().lower()
    return forwarded_ssl in {"on", "1", "true"}


def security_headers(*, is_https: bool = False) -> dict[str, str]:
    """Return security headers for this response.

    ``LEAR_CSP`` lets production deployments ship a stricter CSP without code
    changes. HSTS and CSP's ``upgrade-insecure-requests`` are added only for
    secure/prod contexts so local HTTP desktop development does not get forced
    into HTTPS/WSS and break Uvicorn/WebSocket flows.
    """
    headers = dict(BASE_SECURITY_HEADERS)
    transport_secure = is_https or _is_production()

    csp_override = os.getenv("LEAR_CSP")
    if csp_override:
        csp = csp_override
    else:
        csp = DEFAULT_LOCAL_CONTENT_SECURITY_POLICY
        if transport_secure:
            csp = f"{csp.rstrip('; ')}; upgrade-insecure-requests;"
    headers["Content-Security-Policy"] = csp

    if transport_secure:
        headers["Strict-Transport-Security"] = HSTS_VALUE

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
                headers = self._headers or security_headers(is_https=_scope_is_https(scope))
                for name, value in headers.items():
                    response_headers.setdefault(name, value)
            await send(message)

        await self.app(scope, receive, send_with_security_headers)


def required_security_header_names(*, include_transport_security: bool = False) -> tuple[str, ...]:
    """Header names used by tests/docs.

    Local HTTP responses deliberately omit HSTS, so callers opt into that name
    only when asserting HTTPS/production behavior.
    """
    names = tuple(BASE_SECURITY_HEADERS.keys()) + ("Content-Security-Policy",)
    if include_transport_security:
        names += ("Strict-Transport-Security",)
    return names
