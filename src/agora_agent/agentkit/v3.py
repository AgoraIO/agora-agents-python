"""Stored-agent preview and strict mapping from existing immutable builders."""
from __future__ import annotations

import copy
import re
import time
from typing import TYPE_CHECKING, List, Mapping, Optional

from ..v3 import PreconditionFailedError
from ..v3.types import AgentResponse, NumberResponse

if TYPE_CHECKING:
    from .agent import Agent


class UnsupportedFieldError(ValueError):
    def __init__(self, fields):
        self.fields = sorted(set(fields))
        super().__init__("Unsupported v3 fields: " + ", ".join(self.fields))


class NumberNotFoundError(LookupError):
    pass


class SecretRefNotSupportedError(ValueError):
    pass


class SecretRef(str):
    """A validated reference to a write-only project secret."""


def secret_ref(secret_set: str, key: str) -> SecretRef:
    pattern = r"[A-Za-z0-9_]{1,64}"
    if not isinstance(secret_set, str) or not re.fullmatch(pattern, secret_set):
        raise ValueError("secret_set must contain 1-64 letters, digits, underscores")
    if not isinstance(key, str) or not re.fullmatch(pattern, key):
        raise ValueError("key must contain 1-64 letters, digits, underscores")
    return SecretRef(f"$secrets.{secret_set}.{key}")


def guard_v2(value):
    if isinstance(value, str) and value.startswith("$secrets."):
        raise SecretRefNotSupportedError("secret_ref requires save() or deploy()")
    if isinstance(value, Mapping):
        for item in value.values():
            guard_v2(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            guard_v2(item)
    elif hasattr(value, "model_dump"):
        guard_v2(value.model_dump(exclude_none=True))


def variable_definition(name, definition=None, **fields):
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name):
        raise ValueError("Variable name must match ^[a-z][a-z0-9_]{0,63}$")
    result = {**(definition or {}), **fields}
    unknown = set(result) - {"type", "required", "options", "extract", "description"}
    if unknown:
        raise ValueError("Unknown variable fields: " + ", ".join(sorted(unknown)))
    if result.get("type") not in ("str", "int", "float", "bool", "date", "datetime"):
        raise ValueError("Variable type must be str, int, float, bool, date or datetime")
    for key in ("extract", "required"):
        if key in result and not isinstance(result[key], bool):
            raise ValueError(key + " must be a bool")
    description = result.get("description")
    if description is not None and (not isinstance(description, str) or len(description) > 2000):
        raise ValueError("description must be a string of at most 2000 characters")
    if result.get("extract") and (not isinstance(description, str) or not description.strip()):
        raise ValueError("Extracted variables require a nonempty description")
    if "options" in result:
        options = result["options"]
        if not isinstance(options, list) or not 1 <= len(options) <= 100:
            raise ValueError("options must contain 1-100 unique primitive values")
        if any(not isinstance(v, (str, int, float, bool)) for v in options) or len({(bool if isinstance(v, bool) else str if isinstance(v, str) else float, v) for v in options}) != len(options):
            raise ValueError("options must contain unique primitive values")
    return copy.deepcopy(result)


def dump(value):
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if isinstance(value, dict):
        return {k: dump(v) for k, v in value.items() if v is not None}
    if isinstance(value, (tuple, list)):
        return [dump(v) for v in value]
    return copy.deepcopy(value)


def module(config, category, errors):
    config = dump(config)
    params = dict(config.pop("params", {}) or {})
    if category == "tts" and config.get("vendor") == "minimax":
        preset_model = config.pop("_minimax_preset_model", None)
        if preset_model is not None:
            params.setdefault("model", preset_model)
    if category == "llm" and config.get("style") == "bedrock":
        config.setdefault("vendor", "amazon")
        if "region" in config:
            params.setdefault("region", config.pop("region"))
    vendor = config.get("vendor")
    provider_fields = {
        ("asr", "amazon"): ("access_key_id", "secret_access_key"),
        ("asr", "google"): ("adc_credentials_string",),
        ("asr", "microsoft"): ("key",),
        ("asr", "speechmatics"): ("key",),
        ("llm", "amazon"): ("api_key", "access_key", "secret_key"),
        ("tts", "amazon"): ("aws_access_key_id", "aws_secret_access_key"),
        ("tts", "google"): ("credentials",),
        ("tts", "sarvam"): ("api_subscription_key",),
        **{("tts", name): ("key",) for name in ("elevenlabs", "humeai", "microsoft", "minimax")},
        ("avatar", "sensetime"): ("app_key",),
        ("avatar", "spatius"): ("spatius_api_key",),
    }.get((category, vendor), ("api_key",))
    fields = {}
    all_credentials = {"api_key", "key", "api_subscription_key", "app_key", "spatius_api_key", "access_key_id", "secret_access_key", "aws_access_key_id", "aws_secret_access_key", "access_key", "secret_key", "adc_credentials_string", "service_account", "credentials"}
    for source in (config, params):
        for field in tuple(source):
            if field not in all_credentials:
                continue
            value = source.pop(field)
            target = field if field in provider_fields else provider_fields[0] if field in {"api_key", "key", "api_subscription_key"} and len(provider_fields) == 1 else None
            if target is None:
                errors.append(category + ".credential." + field)
            elif target in fields and fields[target] != value:
                errors.append(category + ".credential (multiple different " + target + " values)")
            else:
                fields[target] = value
    result = {"credential": {"mode": "byok", "fields": fields} if fields else {"mode": "managed"}}
    allowed = {
        "asr": {"vendor", "url", "model", "language"},
        "llm": {"vendor", "url", "style", "model", "input_modalities", "output_modalities", "max_history", "failure_message", "tools", "mcp_servers", "headers"},
        "tts": {"vendor", "url", "skip_patterns", "headers"},
        "avatar": {"vendor", "url", "enabled"},
    }[category]
    # v2 provider serializers keep endpoints and ASR/LLM model choices in params.
    for field in ("url", "model"):
        if field in params and field in allowed:
            result[field] = params.pop(field)
    if "base_url" in params and "url" not in result:
        result["url"] = params.pop("base_url")
    if category == "avatar" and "enable" in config:
        config["enabled"] = config.pop("enable")
    for field, value in config.items():
        if field not in allowed:
            errors.append(category + "." + field)
        else:
            result[field] = value
    if category == "tts" and any(not isinstance(v, str) for v in result.get("skip_patterns", [])):
        errors.append("tts.skip_patterns (numeric v2 patterns have no confirmed v3 mapping)")
    if not fields:
        result.pop("url", None)
        for key in ("url", "base_url"):
            params.pop(key, None)
    if params:
        result["params"] = params
    return result


def _turn(config, interruption, errors):
    config = dump(config or {})
    result = {}
    nested = config.pop("config", {}) or {}
    if config.get("mode") == "default":
        config.pop("mode")
    if "speech_threshold" in nested:
        result["speech_threshold"] = nested.pop("speech_threshold")
    if config.get("type") == "agora_vad":
        config.pop("type")
        start = {k: config.pop(k) for k in ("interrupt_duration_ms", "prefix_padding_ms") if k in config}
        end = {k: config.pop(k) for k in ("silence_duration_ms",) if k in config}
        if start:
            nested.setdefault("start_of_speech", {"mode": "vad", "vad_config": start})
        if end:
            nested.setdefault("end_of_speech", {"mode": "vad", "vad_config": end})
        if "threshold" in config:
            result["speech_threshold"] = config.pop("threshold")
        interrupt_mode = config.pop("interrupt_mode", None)
        if interrupt_mode in ("append", "ignore"):
            result["interruption"] = {"mode": "off", "when_off": interrupt_mode}
        elif interrupt_mode == "keyword":
            result["interruption"] = {"mode": "keywords", "keywords": config.pop("interrupt_keywords", [])}
        elif interrupt_mode == "interrupt":
            result["interruption"] = {"mode": "start_of_speech"}
        elif interrupt_mode is not None:
            errors.append("turn_detection.interrupt_mode")
    config.pop("language", None)  # ASR language, not a v3 turn-detection field.
    for key in ("start_of_speech", "end_of_speech"):
        boundary = dump(nested.pop(key, config.pop(key, None)))
        if boundary is None:
            continue
        mode = boundary.pop("mode", boundary.pop("type", None))
        if key == "start_of_speech" and mode in ("keywords", "disabled"):
            if mode == "keywords":
                keywords = boundary.pop("keywords_config", {})
                result["interruption"] = {"mode": "keywords", "keywords": keywords.get("trigger_keywords", keywords.get("triggered_keywords", keywords.get("keywords", [])))}
            else:
                disabled = boundary.pop("disabled_config", {})
                result["interruption"] = {"mode": "off", "when_off": disabled.get("strategy", "append")}
            if boundary:
                errors.extend("turn_detection." + key + "." + k for k in boundary)
            continue
        flat = {"type": mode}
        for field, value in boundary.items():
            if field in ("vad_config", "semantic_config"):
                flat.update(value)
            else:
                flat[field] = value
        if flat.get("max_wait_ms", 500) < 500:
            errors.append("turn_detection.end_of_speech.max_wait_ms")
        result[key] = flat
    if nested:
        errors.extend("turn_detection.config." + k for k in nested)
    if "speech_threshold" in config:
        result["speech_threshold"] = config.pop("speech_threshold")
    if config:
        errors.extend("turn_detection." + k for k in config)
    if interruption is not None:
        incoming = dump(interruption)
        enabled = incoming.pop("enable", True)
        mode = incoming.pop("mode", "start_of_speech")
        disabled = incoming.pop("disabled_config", {})
        keywords = incoming.pop("keywords_config", {})
        if enabled is False or mode in ("disabled", "off"):
            converted = {"mode": "off", "when_off": disabled.get("strategy", incoming.pop("strategy", incoming.pop("when_off", "append")))}
        elif mode == "keywords":
            converted = {"mode": "keywords", "keywords": keywords.get("trigger_keywords", keywords.get("triggered_keywords", incoming.pop("keywords", [])))}
        else:
            converted = {"mode": mode}
        errors.extend("interruption." + k for k in incoming)
        result["interruption"] = converted
    return result


def build_body(agent, name=None):
    if agent._mllm is not None:
        raise UnsupportedFieldError(["mllm (realtime pipelines are not supported by the preview API)"])
    errors = []
    for field in ("sal", "advanced_features", "geofence", "labels", "rtc", "pipeline_id"):
        if getattr(agent, "_" + field, None) is not None:
            errors.append(field)
    params = dump(agent._parameters or {})
    errors.extend("parameters." + k for k in params if k != "silence_config")
    result = {"agent_name": name if name is not None else f"agent-{time.time_ns()}"}
    if not isinstance(result["agent_name"], str) or not result["agent_name"].strip():
        raise ValueError("name must be nonempty")
    pipeline = {"mode": "cascaded"}
    conversational = dump(agent._resolve_llm_config()) or {}
    messages = conversational.pop("system_messages", None)
    if messages is not None:
        source = "llm.system_messages"
        if not isinstance(messages, list):
            errors.append(source)
        else:
            valid = []
            for index, message in enumerate(messages):
                if not isinstance(message, dict) or set(message) != {"role", "content"} or message.get("role") not in {"system", "user", "assistant"} or not isinstance(message.get("content"), str):
                    errors.append(f"{source}[{index}]")
                else:
                    valid.append(message)
            system = [m["content"] for m in valid if m["role"] == "system"]
            if system:
                result["instructions"] = "\n".join(system)
            non_system = [m for m in valid if m["role"] != "system"]
            if non_system:
                result["messages"] = non_system
    if "instructions" not in result and agent._instructions is not None:
        result["instructions"] = agent._instructions
    greeting_text = conversational.pop("greeting_message", agent._greeting)
    greeting_url = conversational.pop("greeting_audio_url", None)
    greeting = dump(conversational.pop("greeting_configs", agent._greeting_configs) or {})
    if "audio_download_timeout_ms" in greeting:
        greeting["download_timeout_ms"] = greeting.pop("audio_download_timeout_ms")
    if "audio_pcm_sample_rate" in greeting:
        greeting["pcm_sample_rate"] = greeting.pop("audio_pcm_sample_rate")
    errors.extend("greeting_configs." + k for k in greeting if k not in {"mode", "on", "delay_ms", "download_timeout_ms", "pcm_sample_rate"})
    if "mode" in greeting:
        mode = greeting.pop("mode")
        mapped = {"single_every": "each_join", "single_first": "first_join", "each_join": "each_join", "first_join": "first_join"}.get(mode) if isinstance(mode, str) else None
        if mapped is None or ("on" in greeting and greeting["on"] != mapped):
            errors.append("greeting_configs.mode")
        else:
            greeting["on"] = mapped
    if "on" in greeting and greeting["on"] not in ("each_join", "first_join"):
        errors.append("greeting_configs.on")
    if not greeting_url:
        errors.extend("greeting_configs." + key for key in ("download_timeout_ms", "pcm_sample_rate") if key in greeting)
    if greeting_url and not greeting_text:
        errors.append("greeting_audio_url (v3 requires companion greeting text)")
    if greeting_url or greeting_text is not None:
        result["greeting"] = {"mode": "audio" if greeting_url else "text", "text": greeting_text or "", **greeting}
        if greeting_url:
            result["greeting"]["url"] = greeting_url
    elif greeting:
        errors.append("greeting_configs (requires greeting)")
    if conversational.pop("template_variables", None):
        errors.append("llm.template_variables (use with_variable)")
    td = _turn(agent._turn_detection, agent._interruption, errors)
    if td:
        pipeline["turn_detection"] = td
    if conversational:
        pipeline["llm"] = module(conversational, "llm", errors)
    for source, target in (("stt", "asr"), ("tts", "tts"), ("avatar", "avatar")):
        value = getattr(agent, "_" + source, None)
        if target == "asr":
            language = agent._field_value(agent._turn_detection, "language")
            if value is not None or language is not None:
                # Preserve v2 interaction-language precedence and its existing
                # managed ASR fallback, without adding ASR to partial builders.
                value = agent._resolve_asr_config(agent._resolve_turn_detection_config())
        if value is not None:
            pipeline[target] = module(value, target, errors)
    if "silence_config" in params:
        pipeline["silence_config"] = {"enabled": True, **params["silence_config"]}
    if agent._filler_words is not None:
        filler = dump(agent._filler_words)
        for key, nested in (("trigger", "fixed_time_config"), ("content", "static_config")):
            if key in filler:
                part = filler[key]
                sub = part.pop(nested, {})
                generated = part.pop("generated_config", {})
                if "prompt" in generated:
                    generated["instructions"] = generated.pop("prompt")
                generated.pop("llm_provider", None)
                part.update(sub)
                part.update(generated)
        result["filler_words"] = filler
    variables = getattr(agent, "_v3_variables", {})
    if variables:
        result["variables"] = copy.deepcopy(variables)
    result["pipeline"] = pipeline
    if errors:
        raise UnsupportedFieldError(errors)
    return result


_MUTABLE = {"agent_name", "instructions", "messages", "greeting", "variables", "pipeline", "filler_words"}


def replacement_patch(previous, desired, category=None):
    """Clear readable stale keys recursively. Never echo IDs or credential metadata."""
    result = copy.deepcopy(desired)
    # Responses hide credential fields. Clear the known old vendor's field names
    # before merging a new vendor, so hidden write-only keys cannot survive.
    if isinstance(previous.get("credential"), dict) and isinstance(desired.get("credential"), dict) and desired["credential"].get("mode") == "byok":
        old_fields = {
            ("asr", "amazon"): {"access_key_id", "secret_access_key"},
            ("asr", "google"): {"adc_credentials_string"},
            ("asr", "microsoft"): {"key"}, ("asr", "speechmatics"): {"key"},
            ("llm", "amazon"): {"api_key", "access_key", "secret_key"},
            ("tts", "amazon"): {"aws_access_key_id", "aws_secret_access_key"},
            ("tts", "google"): {"credentials"}, ("tts", "sarvam"): {"api_subscription_key"},
            **{("tts", vendor): {"key"} for vendor in ("elevenlabs", "humeai", "microsoft", "minimax")},
            ("avatar", "sensetime"): {"app_key"}, ("avatar", "spatius"): {"spatius_api_key"},
        }.get((category, previous.get("vendor")), {"api_key"})
        result["credential"]["fields"] = {**{field: None for field in old_fields}, **result["credential"].get("fields", {})}
    for key, old in previous.items():
        if key not in result:
            result[key] = None
        elif isinstance(old, dict) and isinstance(result[key], dict):
            if key == "credential":
                if result[key].get("mode") == "managed":
                    result[key]["fields"] = None
                continue  # Resolved credentials have read-only metadata and hide API keys.
            result[key] = replacement_patch(old, result[key], key if key in {"asr", "llm", "tts", "avatar"} else category)
    return result


def _require_etag(response):
    if not response.etag:
        raise ValueError("v3 response omitted ETag; refusing an unguarded update")
    return response.etag


def _require_client(agent, async_):
    from ..pool_client import Agora, AsyncAgora
    expected = AsyncAgora if async_ else Agora
    if not isinstance(agent._client, expected):
        raise TypeError("save_async requires AsyncAgora" if async_ else "save requires Agora")


def save(agent, *, name=None, agent_id=None) -> SavedAgent:
    _require_client(agent, False)
    body = build_body(agent, name)
    from ..v3.contract import _extras
    _extras(body, saved=True)
    raw = agent._client.v3.agents.with_raw_response
    if agent_id is None:
        response = raw.create(**body)
    else:
        previous = raw.get(agent_id=agent_id)
        old = {k: v for k, v in previous.data.items() if k in _MUTABLE}
        body = replacement_patch(old, body)
        response = raw.update(agent_id=agent_id, if_match=_require_etag(previous), **body)
    return SavedAgent(agent._client, response)


async def save_async(agent, *, name=None, agent_id=None) -> AsyncSavedAgent:
    _require_client(agent, True)
    body = build_body(agent, name)
    from ..v3.contract import _extras
    _extras(body, saved=True)
    raw = agent._client.v3.agents.with_raw_response
    if agent_id is None:
        response = await raw.create(**body)
    else:
        previous = await raw.get(agent_id=agent_id)
        old = {k: v for k, v in previous.data.items() if k in _MUTABLE}
        response = await raw.update(agent_id=agent_id, if_match=_require_etag(previous), **replacement_patch(old, body))
    return AsyncSavedAgent(agent._client, response)


def _normalize(number):
    return re.sub(r"[\s().-]", "", number)


def _number_id(number):
    if isinstance(number, Mapping):
        return number["number_id"]
    if not isinstance(number, str) or not number.strip():
        raise ValueError("number must be a number ID, E.164 string or v3 number object")
    return number


def _policy(max_call_duration_seconds, max_silence_duration_ms):
    policy = {}
    for key, value in (("max_call_duration_seconds", max_call_duration_seconds), ("max_silence_duration_ms", max_silence_duration_ms)):
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(key + " must be a positive integer")
            policy[key] = value
    return policy


class _SavedAgentBase:
    def __init__(self, client, response):
        self._client = client
        self.id: str = response.data["agent_id"]
        self.name: str = response.data["agent_name"]
        self.etag: Optional[str] = response.etag
        self.data: AgentResponse = response.data
        self.raw = client.v3.agents

class SavedAgent(_SavedAgentBase):
    def create_session(self, *, channel: str, agent_uid: Optional[str] = None, remote_uids: Optional[List[str]] = None,
                       name=None, client_reference=None, idle_timeout=None,
                       max_duration=None, labels=None, values=None, idempotency_key=None, token=None,
                       encryption=None, audio_scenario=None, graceful_stop=None, data_policy=None, geofence=None, debug=None, warn=None):
        from .session_backend import create_session
        return create_session(self, channel=channel, agent_uid=agent_uid,
            remote_uids=remote_uids, name=name, client_reference=client_reference,
            idle_timeout=idle_timeout, max_duration=max_duration, labels=labels,
            values=values, idempotency_key=idempotency_key, token=token, encryption=encryption,
            audio_scenario=audio_scenario, graceful_stop=graceful_stop, data_policy=data_policy, geofence=geofence,
            debug=debug, warn=warn)

    @classmethod
    def get(cls, client, agent_id) -> SavedAgent:
        return cls(client, client.v3.agents.with_raw_response.get(agent_id=agent_id))

    def update(self, config: Agent, *, name: Optional[str] = None) -> SavedAgent:
        """Save a replacement configuration to this ID, preserving its name."""
        if config._client is not self._client:
            raise ValueError("SavedAgent.update requires a configuration bound to the same client")
        return config.save(name=self.name if name is None else name, agent_id=self.id)

    def delete(self):
        return self.raw.delete(agent_id=self.id)

    def list_numbers(self) -> List[NumberResponse]:
        """Scan project number pages and return numbers assigned to this agent."""
        return [
            number for number in self._client.v3.numbers.iter_all(limit=100)
            if (number.get("inbound") or {}).get("agent") == self.id
        ]

    def _resolve_number(self, number):
        identifier = _number_id(number)
        if identifier.startswith("+"):
            cursor = None
            seen = set()
            while True:
                page = self._client.v3.numbers.list(limit=100, cursor=cursor)
                for item in page["data"]["list"]:
                    if _normalize(item["number"]) == _normalize(identifier):
                        return item["number_id"]
                if not page.get("has_more"):
                    break
                cursor = page.get("next_cursor")
                if not cursor or cursor in seen:
                    raise ValueError("Invalid or repeated number pagination cursor")
                seen.add(cursor)
            raise NumberNotFoundError(f"Number {identifier} not found in project {self._client.app_id}")
        return identifier

    def _assign(self, number, agent_id, policy):
        identifier = self._resolve_number(number)
        raw = self._client.v3.numbers.with_raw_response
        for attempt in range(2):
            previous = raw.get(number_id=identifier)
            inbound = {"agent": agent_id}
            if policy:
                inbound["call_policy"] = policy
            try:
                return raw.update(number_id=identifier, if_match=_require_etag(previous), inbound=inbound).data
            except PreconditionFailedError:
                if attempt:
                    raise

    def assign_number(self, number, *, max_call_duration_seconds=None, max_silence_duration_ms=None) -> NumberResponse:
        return self._assign(number, self.id, _policy(max_call_duration_seconds, max_silence_duration_ms))

    def unassign_number(self, number) -> NumberResponse:
        return self._assign(number, None, {})


class AsyncSavedAgent(_SavedAgentBase):
    def create_session(self, *, channel: str, agent_uid: Optional[str] = None, remote_uids: Optional[List[str]] = None,
                       name=None, client_reference=None, idle_timeout=None,
                       max_duration=None, labels=None, values=None, idempotency_key=None, token=None,
                       encryption=None, audio_scenario=None, graceful_stop=None, data_policy=None, geofence=None, debug=None, warn=None):
        from .session_backend import create_session
        return create_session(self, asynchronous=True, channel=channel,
            agent_uid=agent_uid, remote_uids=remote_uids, name=name,
            client_reference=client_reference, idle_timeout=idle_timeout,
            max_duration=max_duration, labels=labels, values=values, idempotency_key=idempotency_key,
            token=token, encryption=encryption, audio_scenario=audio_scenario, graceful_stop=graceful_stop,
            data_policy=data_policy, geofence=geofence, debug=debug, warn=warn)

    create_async_session = create_session

    @classmethod
    async def get(cls, client, agent_id) -> AsyncSavedAgent:
        return cls(client, await client.v3.agents.with_raw_response.get(agent_id=agent_id))

    async def update(self, config: Agent, *, name: Optional[str] = None) -> AsyncSavedAgent:
        """Save a replacement configuration to this ID, preserving its name."""
        if config._client is not self._client:
            raise ValueError("AsyncSavedAgent.update requires a configuration bound to the same client")
        return await config.save_async(name=self.name if name is None else name, agent_id=self.id)

    async def delete(self):
        return await self.raw.delete(agent_id=self.id)

    async def list_numbers(self) -> List[NumberResponse]:
        """Scan project number pages and return numbers assigned to this agent."""
        return [
            number async for number in self._client.v3.numbers.iter_all(limit=100)
            if (number.get("inbound") or {}).get("agent") == self.id
        ]

    async def _resolve_number(self, number):
        identifier = _number_id(number)
        if identifier.startswith("+"):
            cursor = None
            seen = set()
            while True:
                page = await self._client.v3.numbers.list(limit=100, cursor=cursor)
                for item in page["data"]["list"]:
                    if _normalize(item["number"]) == _normalize(identifier):
                        return item["number_id"]
                if not page.get("has_more"):
                    break
                cursor = page.get("next_cursor")
                if not cursor or cursor in seen:
                    raise ValueError("Invalid or repeated number pagination cursor")
                seen.add(cursor)
            raise NumberNotFoundError(f"Number {identifier} not found in project {self._client.app_id}")
        return identifier

    async def _assign(self, number, agent_id, policy):
        identifier = await self._resolve_number(number)
        raw = self._client.v3.numbers.with_raw_response
        for attempt in range(2):
            previous = await raw.get(number_id=identifier)
            inbound = {"agent": agent_id}
            if policy:
                inbound["call_policy"] = policy
            try:
                return (await raw.update(number_id=identifier, if_match=_require_etag(previous), inbound=inbound)).data
            except PreconditionFailedError:
                if attempt:
                    raise

    async def assign_number(self, number, *, max_call_duration_seconds=None, max_silence_duration_ms=None) -> NumberResponse:
        return await self._assign(number, self.id, _policy(max_call_duration_seconds, max_silence_duration_ms))

    async def unassign_number(self, number) -> NumberResponse:
        return await self._assign(number, None, {})

# Compatibility names are exact aliases; all paths share the same implementation.
DeployedAgent = SavedAgent
AsyncDeployedAgent = AsyncSavedAgent
deploy = save
deploy_async = save_async
