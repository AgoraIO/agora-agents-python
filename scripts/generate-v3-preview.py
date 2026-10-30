"""Generate Python wire TypedDicts/resources from root openapi.json (not Fern).

Transport, validators and AgentKit adapters are handwritten. The packaged JSON is
an identical runtime copy of the input; root openapi.yaml is the shared handoff.
"""
import json
import keyword
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src/agora_agent/v3"
spec = json.loads((ROOT / "openapi.json").read_text())
schemas = spec["components"]["schemas"]

def ref(node):
    while "$ref" in node:
        obj = spec
        for part in node["$ref"][2:].split("/"):
            obj = obj[part.replace("~1", "/").replace("~0", "~")]
        node = obj
    return node

def typ(node):
    if "$ref" in node:
        return node["$ref"].split("/")[-1]
    if "const" in node:
        return f"Literal[{node['const']!r}]"
    if "enum" in node:
        return "Literal[" + ", ".join(repr(x) for x in node["enum"]) + "]"
    for key in ("anyOf", "oneOf"):
        if key in node:
            return "Union[" + ", ".join(typ(x) for x in node[key]) + "]"
    kind = node.get("type")
    if kind == "array":
        return "List[" + typ(node.get("items", {})) + "]"
    if kind == "object":
        value = node.get("additionalProperties")
        if not isinstance(value, dict):
            value = next(iter(node.get("patternProperties", {}).values()), {})
        return "Dict[str, " + typ(value) + "]"
    return {"string": "str", "integer": "int", "number": "float", "boolean": "bool", "null": "None"}.get(kind, "Any")

lines = ['"""Generated wire types from root openapi.json; constraints live in the shared contract."""',
         'from __future__ import annotations', 'from typing import Any, Dict, List, Union',
         'from typing_extensions import Literal, Required, TypedDict', '']
aliases = []
for name, node in schemas.items():
    if "$ref" in node:
        aliases.append(f"{name} = {typ(node)}")
        continue
    if "properties" not in node:
        aliases.append(f"{name} = {typ(node)}")
        continue
    props = node["properties"]
    fields = [(key, ("Required[" + typ(value) + "]") if key in node.get("required", []) else typ(value)) for key, value in props.items()]
    if any(keyword.iskeyword(key) or not key.isidentifier() for key, _ in fields):
        # Only telephony transports contain reserved Python keys. Quoted refs
        # retain forward annotations while preserving required scalar fields.
        parts = []
        for key, value in fields:
            expr = value
            if value.startswith("Required["):
                expr = "Required[" + repr(value[9:-1]) + "]"
            else:
                expr = repr(value)
            parts.append(repr(key) + ": " + expr)
        lines.append(f"{name} = TypedDict({name!r}, {{{', '.join(parts)}}}, total=False)")
    else:
        lines += [f"class {name}(TypedDict, total=False):"] + ([f"    {key}: {value}" for key, value in fields] or ["    pass"])
    lines.append("")
lines += [re.sub(r"(?<![\w\"\'])\b(JsonValue|AgentRequest_JsonValue)\b", lambda m: repr(m[0]), line) if not line.startswith(("JsonValue =", "AgentRequest_JsonValue =")) else line for line in aliases]
lines += ['''
# Compatibility names retained for the additive preview namespace.
AgentCreateModel = AgentCreateInput
AgentPatchRequest = AgentPatch
SessionLifecycle = Lifecycle
EphemeralSessionAgent = PublicAgentInput
StartSessionResponse = SessionStartResponse
class RtcGeofence(TypedDict, total=False):
    area: Required[Literal["global", "north_america", "europe", "asia", "india", "japan"]]
    exclude_area: Literal["north_america", "europe", "asia", "india", "japan"]
class RtcSessionTransport(RtcTransport, total=False):
    geofence: RtcGeofence
SessionTransport = Union[RtcSessionTransport, TelephonyTransport]
''']
names = list(schemas) + ["AgentCreateModel", "AgentPatchRequest", "SessionLifecycle", "EphemeralSessionAgent", "StartSessionResponse", "RtcGeofence", "RtcSessionTransport", "SessionTransport"]
lines += ["__all__ = " + repr(names), ""]
(OUT / "types.py").write_text("\n".join(lines))

classes: Dict[str, List[tuple]] = {key: [] for key in ("agents", "secrets", "numbers", "sessions", "campaigns")}
for path, operations in spec["paths"].items():
    tail = path.split("{appid}/", 1)[1]
    resource = tail.split("/", 1)[0]
    if resource not in classes:
        continue
    for verb, op in operations.items():
        if verb not in {"get", "post", "put", "patch", "delete"}:
            continue
        method = {"get": "get" if "/" in tail else "list", "post": "create", "put": "replace", "patch": "update", "delete": "delete"}[verb]
        if "/keys/" in tail:
            method = "set_key" if verb == "put" else "delete_key"
        if resource == "sessions" and verb == "post":
            method = "start_ephemeral" if tail.endswith("/ephemeral") else "stop" if tail.endswith("/stop") else "start"
        if resource == "campaigns" and ":" in tail:
            method = tail.rsplit(":", 1)[1]
        params = [ref(p) for p in op.get("parameters", []) if ref(p)["name"] != "appid"]
        id_name = {"agents": "agent_id", "numbers": "number_id", "campaigns": "campaign_id"}.get(resource, "id")
        rename = {"id": id_name, "If-Match": "if_match", "If-None-Match": "if_none_match", "Idempotency-Key": "idempotency_key"}
        arguments = []
        forwarding = []
        headers = {}
        query = {}
        path_expr = "/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/" + tail
        for p in params:
            key = rename.get(p["name"], p["name"])
            ptype = typ(p.get("schema", {"type": "string"}))
            required = p.get("required", False)
            arguments.append(f"{key}: {ptype}" if required else f"{key}: Optional[{ptype}] = None")
            forwarding.append(key)
            if p["in"] == "path":
                path_expr = path_expr.replace("{" + p["name"] + "}", "{segment(" + key + ")}")
            if p["in"] == "query":
                query[p["name"]] = key
            if p["in"] == "header":
                headers[p["name"]] = key
        request = op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
        body_fields = []
        if request:
            body_schema = ref(request)
            for key, node in body_schema.get("properties", {}).items():
                ptype = "SessionTransport" if resource == "sessions" and key == "transport" and verb == "post" else typ(node)
                required = key in body_schema.get("required", [])
                arguments.append(f"{key}: {ptype}" if required else f"{key}: {ptype} = _UNSET")
                forwarding.append(key)
                body_fields.append(key)
        output = next(ref(r).get("content", {}).get("application/json", {}).get("schema", {}) for code, r in op["responses"].items() if code.startswith("2"))
        result = typ(output)
        classes[resource].append((method, arguments, forwarding, verb.upper(), path_expr, headers, query, body_fields, result))

text = ['"""Generated resources from root openapi.json; shared token transport is handwritten."""',
        'from __future__ import annotations', 'from typing import Optional',
        'from . import types as T', 'from ._transport import _UNSET, Resource, AsyncResource, RawResponse, segment', '']
# Qualify generated schema references in signatures, retaining Python primitives.
all_names = sorted(names, key=len, reverse=True)
def qualified(value):
    for name in all_names:
        value = re.sub(r"\b" + re.escape(name) + r"\b", "T." + name, value)
    return value
text.insert(3, 'from typing import Any, Dict, List, Union\nfrom typing_extensions import Literal')
for asynchronous in (False, True):
    prefix = "Async" if asynchronous else ""
    for resource, methods in classes.items():
        cname = prefix + resource.title() + "Client"
        raw_name = prefix + resource.title() + "RawClient"
        for raw in (False, True):
            text += [f"class {raw_name if raw else cname}({'AsyncResource' if asynchronous else 'Resource'}):"]
            if not raw:
                text += ['    def __init__(self, owner, options):', '        super().__init__(owner, options)', f'        self.with_raw_response = {raw_name}(owner, options)']
            for method, args, forwarding, verb, path_expr, headers, query, request_fields, result in methods:
                signature = ", ".join([qualified(a) for a in args] + ['appid: Optional[str] = None', 'request_options: Optional[dict] = None'])
                ret = f"RawResponse[{qualified(result)}]" if raw else qualified(result)
                text += [f"    {'async ' if asynchronous else ''}def {method}(self, *, {signature}) -> {ret}:"]
                if raw:
                    expression = lambda value: "{" + ", ".join(repr(k) + ": " + v for k, v in value.items()) + "}"
                    body = "{" + ", ".join(repr(k) + ": " + k for k in request_fields) + "}" if request_fields else "None"
                    text += [f"        return {'await ' if asynchronous else ''}self._request({verb!r}, f{path_expr!r}, body={body}, headers={expression(headers)}, params={expression(query)}, request_options=request_options)"]
                else:
                    call = f"self.with_raw_response.{method}(" + ", ".join(k + "=" + k for k in forwarding + ['appid', 'request_options']) + ")"
                    text += [f"        return {'(await ' + call + ').data' if asynchronous else call + '.data'}"]
                text += [""]
    text += [f"class {prefix}V3Client:", '    def __init__(self, owner, options):']
    for resource in classes:
        text += [f"        self.{resource} = {prefix}{resource.title()}Client(owner, options)"]
    text += [""]
(OUT / "client.py").write_text("\n".join(text))
(OUT / "campaigns.py").write_text('"""Compatibility re-exports of generated campaign resources."""\nfrom .client import CampaignsClient, AsyncCampaignsClient\n__all__ = ["CampaignsClient", "AsyncCampaignsClient"]\n')
(OUT / "openapi.json").write_bytes((ROOT / "openapi.json").read_bytes())
