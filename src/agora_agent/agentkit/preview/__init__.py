"""Preview endpoint support.

Temporary package: delete it when these providers ship on the production
gateway. See ``client.py`` for the routing and gate header.
"""

from .client import (
    PREVIEW_API_BASE_URL,
    PREVIEW_FEATURE_HEADER,
    PreviewFeature,
    PreviewFeatures,
    create_preview_session_clients,
    required_preview_features,
)
from .vendors import (
    GeminiSTT,
    GeminiSTTModels,
)

__all__ = [
    "PREVIEW_API_BASE_URL",
    "PREVIEW_FEATURE_HEADER",
    "GeminiSTTModels",
    "GeminiSTT",
    "PreviewFeature",
    "PreviewFeatures",
    "create_preview_session_clients",
    "required_preview_features",
]
