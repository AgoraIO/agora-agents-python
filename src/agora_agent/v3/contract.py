"""Validate public write shapes against the packaged, shared OpenAPI contract.

Formats (UUID/date-time) remain server validated. No defaults are injected and no
response fields are discarded; this keeps rollout responses forward compatible.
"""
import copy
import ipaddress
import json
import math
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def specification():
    return json.loads(Path(__file__).with_name("openapi.json").read_text())


def _equal(left, right):
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    return left == right


def validate(value, schema, path="body"):
    if schema is True:
        return
    if schema is False:
        raise ValueError(path + " is not allowed")
    if "$ref" in schema:
        target = specification()
        for key in schema["$ref"][2:].split("/"):
            target = target[key.replace("~1", "/").replace("~0", "~")]
        validate(value, target, path)
    for keyword in ("anyOf", "oneOf"):
        if keyword in schema:
            count = 0
            for candidate in schema[keyword]:
                try:
                    validate(value, candidate, path)
                    count += 1
                except ValueError:
                    pass
            if count == 0 or keyword == "oneOf" and count != 1:
                raise ValueError(path + " does not match " + keyword + " in the public contract")
    for candidate in schema.get("allOf", []):
        validate(value, candidate, path)
    if "if" in schema:
        try:
            validate(value, schema["if"], path)
        except ValueError:
            branch = schema.get("else")
        else:
            branch = schema.get("then")
        if branch is not None:
            validate(value, branch, path)
    if "not" in schema:
        try:
            validate(value, schema["not"], path)
        except ValueError:
            pass
        else:
            raise ValueError(path + " contains an unsupported field combination")
    if "const" in schema and not _equal(value, schema["const"]):
        raise ValueError(path + " has an invalid constant")
    if "enum" in schema and not any(_equal(value, item) for item in schema["enum"]):
        raise ValueError(path + " has an invalid enum value")
    kind = schema.get("type")
    matches = {"object": isinstance(value, dict), "array": isinstance(value, list),
               "string": isinstance(value, str), "boolean": isinstance(value, bool),
               "null": value is None,
               "integer": isinstance(value, int) and not isinstance(value, bool),
               "number": isinstance(value, (int, float)) and not isinstance(value, bool)}
    if kind and not matches.get(kind, True):
        raise ValueError(path + " must be " + kind)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(path + "." + key + " is required")
        for limit, compare in (("minProperties", lambda a, b: a < b), ("maxProperties", lambda a, b: a > b)):
            if limit in schema and compare(len(value), schema[limit]):
                raise ValueError(path + " has an invalid number of properties")
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(path + " keys must be strings")
            candidates = ([props[key]] if key in props else []) + [node for pattern, node in patterns.items() if re.search(pattern, key)]
            if not candidates:
                candidates = [schema.get("additionalProperties", True)]
            for candidate in candidates:
                validate(item, candidate, path + "." + key)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", math.inf):
            raise ValueError(path + " has an invalid number of items")
        if schema.get("uniqueItems") and any(_equal(item, previous) for index, item in enumerate(value) for previous in value[:index]):
            raise ValueError(path + " must contain unique items")
        for index, item in enumerate(value):
            validate(item, schema.get("items", {}), f"{path}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", math.inf) or "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise ValueError(path + " has an invalid length or pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
            raise ValueError(path + " is outside its supported range")


def _extras(value, *, saved=False):
    if not isinstance(value, dict):
        return
    credential = value.get("credential")
    if isinstance(credential, dict):
        fields = credential.get("fields")
        if saved and isinstance(fields, dict):
            for item in fields.values():
                if item is not None and (not isinstance(item, str) or re.fullmatch(r"\$secrets\.[A-Za-z0-9_]{1,64}\.[A-Za-z0-9_]{1,64}", item) is None):
                    raise ValueError("Saved BYOK credentials require secret_ref values; inline credentials are allowed only for ephemeral sessions")
    if "allowed_ips" in value and value["allowed_ips"] is not None:
        for address in value["allowed_ips"]:
            try:
                if address == "*":
                    continue
                if "/" in address:
                    host, prefix = address.split("/")
                    if not re.fullmatch(r"0|[1-9][0-9]?", prefix) or int(prefix) > 32:
                        raise ValueError()
                    ipaddress.IPv4Address(host)
                else:
                    ipaddress.IPv4Address(address)
            except (ValueError, TypeError):
                raise ValueError("allowed_ips requires IPv4 addresses, IPv4 CIDRs, or '*'") from None
    for item in value.values():
        if isinstance(item, dict):
            _extras(item, saved=saved)


def validate_write(method, path, body):
    if method in {"GET", "DELETE"} or body is None:
        return
    tail = path.split("/projects/", 1)[-1].split("/", 1)[-1]
    for template, operations in specification()["paths"].items():
        candidate = template.split("{appid}/", 1)[-1]
        pattern = re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(candidate))
        if re.fullmatch(pattern, tail) and method.lower() in operations:
            op = operations[method.lower()]
            schema = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if schema:
                checking = copy.deepcopy(body)
                # Existing optional geofence supplement awaits backend rollout.
                if tail in {"sessions", "sessions/ephemeral"} and isinstance(checking.get("transport"), dict):
                    checking["transport"].pop("geofence", None)
                validate(checking, schema)
                _extras(checking, saved=tail == "agents" or tail.startswith("agents/"))
                if tail == "campaigns" and method == "POST" and len(json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()) > 10 * 1024 * 1024:
                    raise ValueError("Campaign create body exceeds 10 MiB")
                if tail.startswith("sessions/") and method == "PATCH":
                    pipeline = body.get("agent", {}).get("overrides", {}).get("pipeline", {})
                    for module in pipeline.values():
                        if {"url", "base_url", "api_base_url", "endpoint"}.intersection(module.get("params", {})):
                            raise ValueError("Session update cannot change endpoint aliases")
            return
