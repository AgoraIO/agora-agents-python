"""Preview provider vendor classes.

These follow the same shape as the GA vendor classes in ``vendors/`` — snake_case
constructor options in, snake_case wire config out — so they drop into
``agent.with_stt()`` unchanged. Sessions that use them route to the preview
endpoint automatically.
"""

from ..vendors.stt import GeminiSTT, GeminiSTTModels

__all__ = ["GeminiSTTModels", "GeminiSTT"]
