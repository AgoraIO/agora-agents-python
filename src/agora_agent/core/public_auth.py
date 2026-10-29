"""Public SDK authentication policy (including transport overrides)."""
import base64
import binascii
import re


def resolve_client_auth(app_certificate, auth_token, customer_id, customer_secret):
    """Resolve REST authentication independently of optional RTC signing."""
    if customer_id is not None or customer_secret is not None:
        if not all(isinstance(value, str) and value.strip() for value in (customer_id, customer_secret)):
            raise ValueError("Basic authentication requires nonempty customer_id and customer_secret")
        if ":" in customer_id:
            raise ValueError("customer_id must not contain a colon")
        if auth_token is not None:
            raise ValueError("Supply customer_id/customer_secret or auth_token, not both")
        encoded = base64.b64encode(f"{customer_id}:{customer_secret}".encode("utf-8")).decode("ascii")
        return "basic", f"Basic {encoded}"
    if auth_token is not None:
        if not isinstance(auth_token, str) or not auth_token.strip():
            raise ValueError("auth_token must be a nonempty raw token")
        return "token", f"agora token={auth_token}"
    if not isinstance(app_certificate, str) or not app_certificate.strip():
        raise ValueError("app_certificate is required unless auth_token or customer_id/customer_secret is supplied")
    return "app-credentials", ""


def _is_basic_authorization(value):
    match = re.fullmatch(r"Basic ([A-Za-z0-9+/]+={0,2})", value, re.IGNORECASE)
    if match is None:
        return False
    try:
        decoded = base64.b64decode(match.group(1), validate=True).decode("utf-8")
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return False
    username, separator, password = decoded.partition(":")
    return bool(separator and username.strip() and password.strip())


def validate_public_headers(headers, *, allow_empty_authorization=False):
    source = headers or {}
    items = source.multi_items() if hasattr(source, "multi_items") else source.items()
    for name, value in items:
        lower = name.lower()
        if lower.startswith("x-studio-") or lower == "x-consumer-username" or lower.startswith("x-agora-gateway") or lower in {"gateway", "x-gateway-token", "x-gateway-key"}:
            raise ValueError("Internal gateway/region headers are not public: " + name)
        if lower == "idempotency-key" and value is not None and (not isinstance(value, str) or re.fullmatch(r"[!-~]{1,256}", value) is None):
            raise ValueError("Idempotency-Key must contain 1-256 visible ASCII characters")
        if lower == "authorization" and value is not None and not (allow_empty_authorization and value == ""):
            if not re.fullmatch(r"agora token=\S+", str(value), re.IGNORECASE) and not _is_basic_authorization(str(value)):
                raise ValueError("Authorization must use an Agora token or valid Basic credentials")


def validate_public_options(options):
    forbidden = {"customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"}
    if forbidden.intersection(options or {}):
        raise ValueError("Configure Basic credentials with customer_id/customer_secret on the client, or an Authorization header")
    validate_public_headers((options or {}).get("additional_headers", {}))


def validate_effective_public_headers(*sources):
    """Validate the case-insensitive merged headers that will reach HTTPX."""
    merged = merge_public_headers(*sources)
    validate_public_headers(merged)
    if not any(name.lower() == "authorization" for name in merged):
        raise ValueError("Agora token or Basic authorization is required")


def merge_public_headers(*sources):
    """Merge header sources with HTTPX's case-insensitive precedence rules."""
    import httpx

    merged = httpx.Headers()
    for source in sources:
        if not source:
            continue
        items = source.multi_items() if hasattr(source, "multi_items") else source.items()
        merged.update([(name, value) for name, value in items if value is not None])
    return dict(merged)
