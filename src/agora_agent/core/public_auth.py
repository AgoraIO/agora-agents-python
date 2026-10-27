"""Token-only public SDK authentication policy (including transport overrides)."""


def validate_public_headers(headers):
    for name, value in (headers or {}).items():
        lower = name.lower()
        if lower.startswith("x-studio-") or lower == "x-consumer-username" or lower.startswith("x-agora-gateway") or lower in {"gateway", "x-gateway-token", "x-gateway-key"}:
            raise ValueError("Internal gateway/region headers are not public: " + name)
        if lower == "authorization" and value and not str(value).lower().startswith("agora token="):
            raise ValueError("Only Agora token authentication is supported")


def validate_public_options(options):
    forbidden = {"customer_id", "customer_secret", "client_id", "client_secret", "customerId", "customerSecret", "clientId", "clientSecret", "username", "password"}
    if forbidden.intersection(options or {}):
        raise ValueError("Basic credential overrides are not supported")
    validate_public_headers((options or {}).get("additional_headers", {}))
