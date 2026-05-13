from __future__ import annotations

import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class _AsrPresets:
    deepgram_nova_2: str = "deepgram_nova_2"
    deepgram_nova_3: str = "deepgram_nova_3"


@dataclass(frozen=True)
class _LlmPresets:
    openai_gpt_4o_mini: str = "openai_gpt_4o_mini"
    openai_gpt_4_1_mini: str = "openai_gpt_4_1_mini"
    openai_gpt_5_nano: str = "openai_gpt_5_nano"
    openai_gpt_5_mini: str = "openai_gpt_5_mini"


@dataclass(frozen=True)
class _TtsPresets:
    minimax_speech_2_6_turbo: str = "minimax_speech_2_6_turbo"
    minimax_speech_2_8_turbo: str = "minimax_speech_2_8_turbo"
    openai_tts_1: str = "openai_tts_1"


@dataclass(frozen=True)
class _AgentPresets:
    asr: _AsrPresets = _AsrPresets()
    llm: _LlmPresets = _LlmPresets()
    tts: _TtsPresets = _TtsPresets()


AgentPresets = _AgentPresets()

DeepgramPresetModels = ("nova-2", "nova-3")
OpenAIPresetModels = ("gpt-4o-mini", "gpt-4.1-mini", "gpt-5-nano", "gpt-5-mini")
OpenAITtsPresetModels = ("tts-1",)
MiniMaxPresetModels = ("speech-2.6-turbo", "speech_2_6_turbo", "speech-2.8-turbo", "speech_2_8_turbo")

PresetInput = typing.Union[str, typing.Sequence[str]]

_OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
_DEEPGRAM_MODEL_TO_PRESET = {
    "nova-2": AgentPresets.asr.deepgram_nova_2,
    "nova-3": AgentPresets.asr.deepgram_nova_3,
}
_OPENAI_MODEL_TO_PRESET = {
    "gpt-4o-mini": AgentPresets.llm.openai_gpt_4o_mini,
    "gpt-4.1-mini": AgentPresets.llm.openai_gpt_4_1_mini,
    "gpt-5-nano": AgentPresets.llm.openai_gpt_5_nano,
    "gpt-5-mini": AgentPresets.llm.openai_gpt_5_mini,
}
_MINIMAX_MODEL_TO_PRESET = {
    "speech-2.6-turbo": AgentPresets.tts.minimax_speech_2_6_turbo,
    "speech_2_6_turbo": AgentPresets.tts.minimax_speech_2_6_turbo,
    "speech-2.8-turbo": AgentPresets.tts.minimax_speech_2_8_turbo,
    "speech_2_8_turbo": AgentPresets.tts.minimax_speech_2_8_turbo,
}


def _normalize_model_name(value: typing.Any) -> typing.Optional[str]:
    return value.strip().lower() if isinstance(value, str) else None


def _parse_preset_input(preset: typing.Optional[PresetInput]) -> typing.List[str]:
    if preset is None:
        return []
    if isinstance(preset, str):
        return [item.strip() for item in preset.split(",") if item.strip()]
    return [str(item).strip() for item in preset if str(item).strip()]


def normalize_preset_input(preset: typing.Optional[PresetInput]) -> typing.Optional[str]:
    entries = _parse_preset_input(preset)
    return ",".join(entries) if entries else None


def _get_preset_category(preset: str) -> typing.Optional[str]:
    if preset in vars(AgentPresets.asr).values():
        return "asr"
    if preset in vars(AgentPresets.llm).values():
        return "llm"
    if preset in vars(AgentPresets.tts).values():
        return "tts"
    return None


def _omit_none(value: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
    next_value = {k: v for k, v in value.items() if v is not None}
    return next_value or None


def infer_asr_preset(asr: typing.Optional[typing.Dict[str, typing.Any]]) -> typing.Optional[str]:
    if not asr or asr.get("vendor") != "deepgram":
        return None
    params = asr.get("params") or {}
    if params.get("api_key"):
        return None
    return _DEEPGRAM_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or "")


def infer_llm_preset(llm: typing.Optional[typing.Dict[str, typing.Any]]) -> typing.Optional[str]:
    if not llm or llm.get("api_key"):
        return None
    if llm.get("vendor") not in (None, "openai"):
        return None
    if llm.get("url") not in (None, _OPENAI_CHAT_COMPLETIONS_URL):
        return None
    params = llm.get("params") or {}
    return _OPENAI_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or "")


def infer_tts_preset(tts: typing.Optional[typing.Dict[str, typing.Any]]) -> typing.Optional[str]:
    if not tts:
        return None
    vendor = tts.get("vendor")
    params = tts.get("params") or {}
    if vendor == "openai":
        if params.get("api_key"):
            return None
        model = _normalize_model_name(params.get("model")) or "tts-1"
        return AgentPresets.tts.openai_tts_1 if model == "tts-1" else None
    if vendor == "minimax":
        if params.get("key"):
            return None
        return _MINIMAX_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or "")
    return None


def strip_inferred_preset_fields(properties: typing.Dict[str, typing.Any], inferred_presets: typing.Sequence[str]) -> typing.Dict[str, typing.Any]:
    inferred_categories = {
        category for preset in inferred_presets for category in [_get_preset_category(preset)] if category is not None
    }

    asr = properties.get("asr")
    if asr and "asr" in inferred_categories:
        params = dict(asr.get("params") or {})
        inferred_preset = infer_asr_preset(asr)
        if inferred_preset == _DEEPGRAM_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or ""):
            params["model"] = None
        params["api_key"] = None
        asr = {k: v for k, v in {**asr, "params": _omit_none(params)}.items() if v is not None}

    llm = properties.get("llm")
    if llm and "llm" in inferred_categories:
        params = dict(llm.get("params") or {})
        inferred_preset = infer_llm_preset(llm)
        if inferred_preset == _OPENAI_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or ""):
            params["model"] = None
        url = llm.get("url")
        llm = {k: v for k, v in {
            **{k: v for k, v in llm.items() if k not in {"api_key", "url", "params"}},
            "api_key": None,
            "url": url if url and url != _OPENAI_CHAT_COMPLETIONS_URL else None,
            "params": _omit_none(params),
        }.items() if v is not None}

    tts = properties.get("tts")
    if tts and "tts" in inferred_categories:
        params = dict(tts.get("params") or {})
        inferred_preset = infer_tts_preset(tts)
        if tts.get("vendor") == "openai":
            if inferred_preset == AgentPresets.tts.openai_tts_1 and (_normalize_model_name(params.get("model")) or "tts-1") == "tts-1":
                params["model"] = None
            params["api_key"] = None
        elif tts.get("vendor") == "minimax":
            if inferred_preset == _MINIMAX_MODEL_TO_PRESET.get(_normalize_model_name(params.get("model")) or ""):
                params["model"] = None
            params["key"] = None
            params["group_id"] = None
            params["url"] = None
        tts = {k: v for k, v in {**tts, "params": _omit_none(params)}.items() if v is not None}

    return {**properties, "asr": asr, "llm": llm, "tts": tts}


def resolve_session_presets(
    preset: typing.Optional[PresetInput],
    properties: typing.Dict[str, typing.Any],
) -> typing.Tuple[typing.Optional[str], typing.Dict[str, typing.Any]]:
    explicit_presets = _parse_preset_input(preset)
    explicit_categories = {
        category for item in explicit_presets for category in [_get_preset_category(item)] if category is not None
    }
    inferred_presets: typing.List[str] = []

    if "asr" not in explicit_categories:
        inferred = infer_asr_preset(properties.get("asr"))
        if inferred:
            inferred_presets.append(inferred)
    if "llm" not in explicit_categories:
        inferred = infer_llm_preset(properties.get("llm"))
        if inferred:
            inferred_presets.append(inferred)
    if "tts" not in explicit_categories:
        inferred = infer_tts_preset(properties.get("tts"))
        if inferred:
            inferred_presets.append(inferred)

    return (
        normalize_preset_input([*explicit_presets, *inferred_presets]),
        strip_inferred_preset_fields(properties, inferred_presets),
    )
