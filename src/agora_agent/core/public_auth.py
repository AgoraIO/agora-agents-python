"""Token-only public SDK authentication policy (including transport overrides)."""
import re


def validate_public_headers(headers):
    source = headers or {}
    items = source.multi_items() if hasattr(source, "multi_items") else source.items()
    for name, value in items:
        lower = name.lower()
        if lower.startswith("x-studio-") or lower == "x-consumer-username" or lower.startswith("x-agora-gateway") or lower in {"gateway", "x-gateway-token", "x-gateway-key"}:
            raise ValueError("Internal gateway/region headers are not public: " + name)
        if lower == "idempotency-key" and value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Idempotency-Key must be a nonempty string")
        if lower == "authorization" and value and not re.fullmatch(r"agora token=\S+", str(value), re.IGNORECASE):
            raise ValueError("Only Agora token authentication is supported")


def validate_public_options(options):
    forbidden = {"customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"}
    if forbidden.intersection(options or {}):
        raise ValueError("Basic credential overrides are not supported")
    validate_public_headers((options or {}).get("additional_headers", {}))
