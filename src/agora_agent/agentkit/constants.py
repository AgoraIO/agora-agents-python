"""
Type-safe constants for agent configuration values.
Use these instead of raw strings to avoid typos and get IDE autocomplete.
"""

# Data channel: "rtm" | "datastream"
class DataChannel:
    RTM = "rtm"
    DATASTREAM = "datastream"

class AudioScenario:
    DEFAULT = "default"
    CHORUS = "chorus"
    AISERVER = "aiserver"


# Silence action when timeout elapses: "speak" | "think"
# (Use for parameters.silence_config.action — avoids shadowing SilenceAction type)
class SilenceActionValues:
    SPEAK = "speak"
    THINK = "think"


# SAL mode: "locking" | "recognition"
# (Use for sal.sal_mode — avoids shadowing SalMode type)
class SalModeValues:
    LOCKING = "locking"
    RECOGNITION = "recognition"


# Geofence area: "GLOBAL" | "NORTH_AMERICA" | "EUROPE" | "ASIA" | "INDIA" | "JAPAN"
class GeofenceArea:
    GLOBAL = "GLOBAL"
    NORTH_AMERICA = "NORTH_AMERICA"
    EUROPE = "EUROPE"
    ASIA = "ASIA"
    INDIA = "INDIA"
    JAPAN = "JAPAN"


# Geofence exclude area (when area is GLOBAL)
class GeofenceExcludeArea:
    NORTH_AMERICA = "NORTH_AMERICA"
    EUROPE = "EUROPE"
    ASIA = "ASIA"
    INDIA = "INDIA"
    JAPAN = "JAPAN"


# Filler word selection rule: "shuffle" | "round_robin"
class FillerWordsSelectionRule:
    SHUFFLE = "shuffle"
    ROUND_ROBIN = "round_robin"


# Turn detection type (deprecated; use TurnDetectionNestedConfig.EndOfSpeech instead)
class TurnDetectionTypeValues:
    AGORA_VAD = "agora_vad"
    SERVER_VAD = "server_vad"
    SEMANTIC_VAD = "semantic_vad"


class InterruptionMode:
    START_OF_SPEECH = "start_of_speech"
    KEYWORDS = "keywords"


InterruptionModeStartOfSpeech = InterruptionMode.START_OF_SPEECH
InterruptionModeKeywords = InterruptionMode.KEYWORDS


class InterruptionDisabledStrategy:
    APPEND = "append"
    IGNORE = "ignore"


InterruptionDisabledStrategyAppend = InterruptionDisabledStrategy.APPEND
InterruptionDisabledStrategyIgnore = InterruptionDisabledStrategy.IGNORE


class SpeakPriority:
    INTERRUPT = "INTERRUPT"
    APPEND = "APPEND"
    IGNORE = "IGNORE"


SpeakPriorityInterrupt = SpeakPriority.INTERRUPT
SpeakPriorityAppend = SpeakPriority.APPEND
SpeakPriorityIgnore = SpeakPriority.IGNORE


class MllmTurnDetectionMode:
    AGORA_VAD = "agora_vad"
    SERVER_VAD = "server_vad"
    SEMANTIC_VAD = "semantic_vad"


MllmTurnDetectionModeAgoraVad = MllmTurnDetectionMode.AGORA_VAD
MllmTurnDetectionModeServerVad = MllmTurnDetectionMode.SERVER_VAD
MllmTurnDetectionModeSemanticVad = MllmTurnDetectionMode.SEMANTIC_VAD


# Think action value constants (match Fern wire values)
ThinkOnListeningActionInject = "inject"
ThinkOnListeningActionInterrupt = "interrupt"
ThinkOnListeningActionIgnore = "ignore"
ThinkOnThinkingActionInterrupt = "interrupt"
ThinkOnThinkingActionIgnore = "ignore"
ThinkOnSpeakingActionInterrupt = "interrupt"
ThinkOnSpeakingActionIgnore = "ignore"
