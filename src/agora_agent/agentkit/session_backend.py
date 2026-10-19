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
    return bool(getattr(agent, "_v3_variables", {})) or contains(agent.config)


def create_session(owner, *, asynchronous=False, channel, agent_uid, remote_uids,
                   name=None, client_reference=None, idle_timeout=None, max_duration=None,
                   labels=None, debug=None, warn=None, **unsupported):
    from .agent_session import AgentSession, AsyncAgentSession
    from .v3 import build_body
    invalid = [key for key, value in unsupported.items() if value is not None]
    if invalid:
        raise ValueError("Unsupported session options: " + ", ".join(sorted(invalid)))
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError("channel must be nonempty")
    if not isinstance(agent_uid, str) or not agent_uid.strip():
        raise ValueError("agent_uid must be nonempty")
    if not isinstance(remote_uids, list) or any(not isinstance(v, str) or not v for v in remote_uids):
        raise ValueError("remote_uids must be a list of nonempty strings")
    if name is not None and client_reference is not None and name != client_reference:
        raise ValueError("name and client_reference must agree when both are supplied")
    body = {"transport": {"type": "rtc", "channel": channel, "uid": agent_uid,
                           "subscribe_uids": list(remote_uids)}}
    reference = client_reference if client_reference is not None else name
    if reference is not None:
        body["client_reference"] = reference
    lifecycle = {}
    for key, value in (("idle_timeout_ms", idle_timeout), ("max_duration_ms", max_duration)):
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or value * 1000 != int(value * 1000):
                raise ValueError(key + " must be a nonnegative duration in seconds with millisecond precision")
            lifecycle[key] = int(value * 1000)
    if lifecycle:
        body["lifecycle"] = lifecycle
    stored = hasattr(owner, "id")
    if stored:
        body["agent_id"] = owner.id
        if labels is not None:
            body["labels"] = copy.deepcopy(labels)
    else:
        if labels is not None:
            raise ValueError("labels are not documented for ephemeral sessions")
        agent = build_body(owner)
        agent.pop("agent_name", None)
        body["agent"] = agent
    client = owner._client
    if client is None:
        raise ValueError("client is required")
    session_type = AsyncAgentSession if asynchronous else AgentSession
    return session_type(client=client, agent=owner, app_id=client.app_id,
                        name=reference or "", channel=channel, agent_uid=agent_uid,
                        remote_uids=list(remote_uids), debug=debug, warn=warn,
                        _session_backend={"stored": stored, "body": copy.deepcopy(body)})
