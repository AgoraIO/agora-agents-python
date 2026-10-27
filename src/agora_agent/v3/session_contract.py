"""Validation shared by public session requests and AgentKit's internal adapter."""
import math
import re
import uuid


def _object(value, allowed, field):
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError("Invalid " + field + " fields")


def _integer(value, minimum, maximum, field):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(field + " is outside its supported integer range")


def validate_session(body):
    _object(body, {"agent_id", "agent", "transport", "values", "labels", "lifecycle", "data_policy"}, "session")
    transport = body["transport"]
    if not isinstance(transport, dict):
        raise ValueError("transport must be an object")
    if transport.get("type") == "rtc":
        _validate_rtc_transport(transport)
    elif transport.get("type") == "telephony":
        _validate_telephony_transport(transport)
    else:
        raise ValueError("Unsupported session transport type")
    if body.get("labels") is not None:
        if not isinstance(body["labels"], dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in body["labels"].items()):
            raise ValueError("labels must map strings to strings")
    if body.get("values") is not None:
        if not isinstance(body["values"], dict) or any(not isinstance(k, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", k) or not isinstance(v, (str, int, float, bool)) or isinstance(v, float) and not math.isfinite(v) for k, v in body["values"].items()):
            raise ValueError("values must map variable names to finite JSON primitives")
    if body.get("data_policy") is not None:
        policy = body["data_policy"]
        _object(policy, {"retention"}, "data_policy")
        if policy.get("retention", "30_days") not in {"30_days", "none"}:
            raise ValueError("Unsupported retention")
    if body.get("lifecycle") is not None:
        life = body["lifecycle"]
        _object(life, {"idle_timeout_ms", "max_duration_ms", "graceful_stop"}, "lifecycle")
        for field, minimum in (("idle_timeout_ms", 0), ("max_duration_ms", 1000)):
            if field in life:
                _integer(life[field], minimum, 3600000, field)
        if life.get("graceful_stop") is not None:
            graceful = life["graceful_stop"]
            _object(graceful, {"enabled", "timeout_ms"}, "graceful_stop")
            if "enabled" in graceful and not isinstance(graceful["enabled"], bool):
                raise ValueError("graceful_stop.enabled must be bool")
            if "timeout_ms" in graceful:
                _integer(graceful["timeout_ms"], 0, 120000, "graceful_stop.timeout_ms")


def _validate_rtc_transport(transport):
    _object(transport, {"type", "channel", "uid", "subscribe_uids", "token", "encryption", "audio_scenario", "geofence"}, "transport")
    if not isinstance(transport.get("channel"), str) or not 1 <= len(transport["channel"]) <= 256 or not transport["channel"].strip():
        raise ValueError("channel must contain 1-256 characters")
    uid = transport.get("uid")
    subscribers = transport.get("subscribe_uids")
    if not isinstance(uid, str) or not uid.strip():
        raise ValueError("uid must be a nonempty string")
    if not isinstance(subscribers, list) or len(subscribers) != 1 or not isinstance(subscribers[0], str) or not subscribers[0].strip() or subscribers[0] == "*":
        raise ValueError("subscribe_uids must contain exactly one non-wildcard UID")
    numeric = lambda value: re.fullmatch(r"[0-9]+", value) is not None
    if uid != "0" and numeric(uid) != numeric(subscribers[0]):
        raise ValueError("agent and subscriber must use the same UID type")
    if transport.get("geofence") is not None:
        fence = transport["geofence"]
        _object(fence, {"area", "exclude_area"}, "geofence")
        areas = {"global", "north_america", "europe", "asia", "india", "japan"}
        if fence.get("area") not in areas:
            raise ValueError("Invalid geofence.area")
        if fence.get("exclude_area") is not None and (fence["area"] != "global" or fence["exclude_area"] not in areas - {"global"}):
            raise ValueError("geofence.exclude_area is only supported with global area")
    if "token" in transport and not isinstance(transport["token"], str):
        raise ValueError("RTC token must be a string")
    if transport.get("audio_scenario", "aiserver") not in {"aiserver", "chorus"}:
        raise ValueError("Unsupported audio_scenario")
    if "encryption" in transport:
        enc = transport["encryption"]
        _object(enc, {"mode", "key", "salt"}, "encryption")
        if enc.get("mode") not in {"aes_128_xts", "aes_128_ecb", "aes_256_xts", "sm4_128_ecb", "aes_128_gcm", "aes_256_gcm", "aes_128_gcm2", "aes_256_gcm2"} or not isinstance(enc.get("key"), str) or not enc["key"]:
            raise ValueError("Invalid RTC encryption mode or key")
        if enc.get("salt") is not None and (not isinstance(enc["salt"], str) or not re.fullmatch(r"[A-Za-z0-9+/]{43}=", enc["salt"])):
            raise ValueError("Invalid RTC encryption salt")


def _validate_telephony_transport(transport):
    _object(transport, {"type", "from", "to", "call_policy"}, "telephony transport")
    source = transport.get("from")
    try:
        if not isinstance(source, str) or str(uuid.UUID(source)) != source.lower():
            raise ValueError("invalid UUID")
    except (ValueError, AttributeError):
        raise ValueError("telephony from must be a registered project number UUID") from None
    if not isinstance(transport.get("to"), str) or not re.fullmatch(r"\+[1-9][0-9]{1,14}", transport["to"]):
        raise ValueError("telephony to must be an E.164 phone number")
    policy = transport.get("call_policy")
    if policy is None:
        return
    _object(policy, {"max_ring_duration_ms", "max_call_duration_seconds", "max_silence_duration_ms", "voicemail", "end_call", "transfer"}, "call_policy")
    for field in ("max_ring_duration_ms", "max_call_duration_seconds", "max_silence_duration_ms"):
        if policy.get(field) is not None:
            _integer(policy[field], 1, math.inf, field)
    if policy.get("voicemail") is not None:
        _object(policy["voicemail"], {"mode"}, "voicemail")
        if policy["voicemail"].get("mode") not in {"continue", "hangup"}:
            raise ValueError("Unsupported voicemail mode")
    if policy.get("end_call") is not None:
        end = policy["end_call"]
        _object(end, {"on_conversation_complete", "on_user_request", "on_fax", "on_ai_assistant"}, "end_call")
        if any(not isinstance(v, bool) for v in end.values()):
            raise ValueError("end_call settings must be bool")
    if policy.get("transfer") is not None:
        transfer = policy["transfer"]
        _object(transfer, {"phone_number", "description"}, "transfer")
        if not isinstance(transfer.get("phone_number"), str) or not re.fullmatch(r"\+[1-9][0-9]{1,14}", transfer["phone_number"]):
            raise ValueError("transfer phone_number must be E.164")
        if not isinstance(transfer.get("description"), str) or not 1 <= len(transfer["description"]) <= 1000:
            raise ValueError("transfer requires a description of 1-1000 characters")
