"""Token-only public SDK authentication policy (including transport overrides)."""
import re


def validate_public_headers(headers, *, allow_empty_authorization=False):
    source = headers or {}
    items = source.multi_items() if hasattr(source, "multi_items") else source.items()
    for name, value in items:
        lower = name.lower()
        if lower.startswith("x-studio-") or lower == "x-consumer-username" or lower.startswith("x-agora-gateway") or lower in {"gateway", "x-gateway-token", "x-gateway-key"}:
            raise ValueError("Internal gateway/region headers are not public: " + name)
        if lower == "idempotency-key" and value is not None and (not isinstance(value, str) or re.fullmatch(r"[!-~]{1,256}", value) is None):
            raise ValueError("Idempotency-Key must contain 1-256 visible ASCII characters")
        if lower == "authorization" and value is not None and not (allow_empty_authorization and value == "") and not re.fullmatch(r"agora token=\S+", str(value), re.IGNORECASE):
            raise ValueError("Only Agora token authentication is supported")


def validate_public_options(options):
    forbidden = {"customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"}
    if forbidden.intersection(options or {}):
        raise ValueError("Basic credential overrides are not supported")
    validate_public_headers((options or {}).get("additional_headers", {}))


def validate_effective_public_headers(*sources):
    """Validate the case-insensitive merged headers that will reach HTTPX."""
    merged = merge_public_headers(*sources)
    validate_public_headers(merged)
    if not any(name.lower() == "authorization" for name in merged):
        raise ValueError("Agora token authorization is required")


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
