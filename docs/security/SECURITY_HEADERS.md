# Secure HTTP Headers

Lear's FastAPI bridge installs `SecurityHeadersMiddleware` from
`prash.middleware.security_headers`.

## Applied headers

| Header | Default value | Why it exists |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME sniffing. |
| `X-Frame-Options` | `DENY` | Blocks clickjacking via framing. |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Tells browsers to prefer HTTPS once served over TLS. |
| `Content-Security-Policy` | See middleware constant | Limits script/style/image/font/connect sources. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Reduces cross-origin referrer leakage. |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` | Disables browser APIs the app does not need. |

## CSP compatibility notes

The current demo/admin HTML pages use inline styles and scripts. The default CSP
therefore keeps `'unsafe-inline'` for `script-src` and `style-src` to avoid
breaking existing pages in this pass. The policy still blocks high-risk defaults
with `object-src 'none'`, `base-uri 'self'`, and `frame-ancestors 'none'`.

Deployments can override the policy without code changes:

```bash
export LEAR_CSP="default-src 'self'; object-src 'none'; frame-ancestors 'none'; connect-src 'self' ws: wss:"
```

## Validation

Bash/curl:

```bash
scripts/check_security_headers.sh http://localhost:8000
```

Python cross-platform:

```bash
python scripts/security/check_security_headers.py http://localhost:8000
```

PowerShell:

```powershell
./scripts/check_security_headers.ps1 http://localhost:8000
```
