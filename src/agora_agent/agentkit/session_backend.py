"""Private adapter for the Bruno-documented session lifecycle."""
import copy
import math


def needs_session_backend(agent):
    def contains(value):
        if isinstance(value, str):
            return value.startswith("$secrets.")
        if isinstance(value, dict):
            return any(contains(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return any(contains(v) for v in value)
        return False
    params = agent._parameters or {}
    if hasattr(params, "model_dump"):
        params = params.model_dump(exclude_none=True)
    return bool(getattr(agent, "_v3_variables", {})) or contains(agent.config) or any(key in params for key in ("opt_out", "farewell_config"))


def create_session(owner, *, asynchronous=False, channel, agent_uid, remote_uids,
                   name=None, client_reference=None, idle_timeout=None, max_duration=None,
                   labels=None, values=None, idempotency_key=None, token=None, encryption=None,
                   audio_scenario=None, graceful_stop=None, data_policy=None, geofence=None, debug=None, warn=None, **unsupported):
    from ..pool_client import Agora, AsyncAgora
    from .agent_session import AgentSession, AsyncAgentSession
    from .v3 import build_body, dump
    client = owner._client
    if not isinstance(client, AsyncAgora if asynchronous else Agora):
        raise TypeError("Session requires AsyncAgora" if asynchronous else "Session requires Agora")
    if getattr(client, "area_scope", None) == "cn":
        raise ValueError("Stored and ephemeral sessions in CN are unconfirmed")
    if client_reference is not None:
        raise ValueError("client_reference has been removed; use labels for application metadata")
    invalid = [key for key, value in unsupported.items() if value is not None]
    if invalid:
        raise ValueError("Unsupported session options: " + ", ".join(sorted(invalid)))
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError("channel must be nonempty")
    if not isinstance(agent_uid, str) or not agent_uid.strip():
        raise ValueError("agent_uid must be nonempty")
    if not isinstance(remote_uids, list) or any(not isinstance(v, str) or not v.strip() for v in remote_uids):
        raise ValueError("remote_uids must be a list of nonempty strings")
    body = {"transport": {"type": "rtc", "channel": channel, "uid": agent_uid,
                           "subscribe_uids": list(remote_uids)}}
    reference = name
    fence = geofence if geofence is not None else getattr(owner, "_geofence", None)
    if fence is not None:
        fence = dump(fence)
        body["transport"]["geofence"] = {key: value.lower() if isinstance(value, str) else value for key, value in fence.items()}
    for key, value in (("token", token), ("encryption", encryption), ("audio_scenario", audio_scenario)):
        if value is not None:
            body["transport"][key] = copy.deepcopy(value)
    for key, value in (("values", values), ("labels", labels), ("data_policy", data_policy)):
        if value is not None:
            body[key] = copy.deepcopy(value)
    lifecycle = {}
    for key, value in (("idle_timeout_ms", idle_timeout), ("max_duration_ms", max_duration)):
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or value * 1000 != int(value * 1000):
                raise ValueError(key + " must be a nonnegative duration in seconds with millisecond precision")
            lifecycle[key] = int(value * 1000)
    if graceful_stop is not None:
        lifecycle["graceful_stop"] = copy.deepcopy(graceful_stop)
    if lifecycle:
        body["lifecycle"] = lifecycle
    stored = hasattr(owner, "id")
    if stored:
        body["agent_id"] = owner.id
    else:
        params = dump(owner._parameters or {})
        inline = owner._clone()
        inline._geofence = None
        inline._parameters = {k: v for k, v in params.items() if k not in {"opt_out", "farewell_config", "audio_scenario"}}
        if "opt_out" in params and not isinstance(params["opt_out"], bool):
            raise ValueError("parameters.opt_out must be bool")
        if data_policy is None and "opt_out" in params:
            body["data_policy"] = {"retention": "none" if params["opt_out"] else "30_days"}
        if audio_scenario is None and "audio_scenario" in params:
            body["transport"]["audio_scenario"] = params["audio_scenario"]
        if graceful_stop is None and "farewell_config" in params:
            farewell = params["farewell_config"]
            unknown = set(farewell) - {"graceful_enabled", "graceful_timeout_seconds"}
            if unknown:
                raise ValueError("Unsupported farewell settings: " + ", ".join(sorted(unknown)))
            graceful = {}
            if "graceful_enabled" in farewell:
                graceful["enabled"] = farewell["graceful_enabled"]
            if "graceful_timeout_seconds" in farewell:
                seconds = farewell["graceful_timeout_seconds"]
                if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds * 1000 != int(seconds * 1000):
                    raise ValueError("Invalid farewell timeout in seconds")
                graceful["timeout_ms"] = int(seconds * 1000)
            body.setdefault("lifecycle", {})["graceful_stop"] = graceful
        agent = build_body(inline)
        agent.pop("agent_name", None)
        body["agent"] = agent
    from ..v3.session_contract import validate_session
    validate_session(body)
    if idempotency_key is not None:
        body["idempotency_key"] = idempotency_key
    session_type = AsyncAgentSession if asynchronous else AgentSession
    return session_type(client=client, agent=owner, app_id=client.app_id,
                        name=reference or "", channel=channel, agent_uid=agent_uid,
                        remote_uids=list(remote_uids), debug=debug, warn=warn,
                        _session_backend={"stored": stored, "body": copy.deepcopy(body)})
