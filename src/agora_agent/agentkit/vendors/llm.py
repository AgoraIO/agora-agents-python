from typing import Any, Dict, List, Optional

from .base import BaseLLM
from pydantic import BaseModel, ConfigDict, Field, model_validator

LlmGreetingConfigs = Dict[str, Any]
_OPENAI_MANAGED_MODELS = {"gpt-4o-mini", "gpt-4.1-mini", "gpt-5-nano", "gpt-5-mini"}


def _ensure_mcp_transport(servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ensure each MCP server has transport set (API requires it). Default to streamable_http."""
    result = []
    for s in servers:
        item = dict(s)
        if item.get("transport") is None:
            item["transport"] = "streamable_http"
        result.append(item)
    return result


def _dump_optional_model(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "dict"):
        return value.dict(exclude_none=True)
    return value


class OpenAIOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(..., description="Model name")
    base_url: Optional[str] = Field(default=None, description="Custom base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "OpenAIOptions":
        if not self.model:
            raise ValueError("OpenAI requires model")
        if self.api_key is not None and self.base_url is None:
            raise ValueError("OpenAI requires base_url when api_key is set")
        if self.api_key is None and self.base_url is not None:
            raise ValueError("OpenAI base_url is only valid when api_key is set")
        if self.api_key is None and self.model.strip().lower() not in _OPENAI_MANAGED_MODELS:
            raise ValueError("OpenAI requires api_key unless using a supported Agora-managed model")
        if self.api_key is None and self.vendor is not None:
            raise ValueError("OpenAI Agora-managed mode does not allow vendor")
        return self


class OpenAI(OpenAIOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        # model is the default; explicit params entries extend/override it.
        # This matches the TS SDK behaviour: { model, ...params }.
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        # Named fields take precedence over anything in the generic params dict.
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class AzureOpenAIOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Azure OpenAI API key")
    model: str = Field(..., description="Azure deployment model name")
    endpoint: str = Field(..., description="Azure endpoint URL")
    deployment_name: str = Field(..., description="Azure deployment name")
    api_version: str = Field(default="2024-08-01-preview", description="Azure API version")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")


class AzureOpenAI(AzureOpenAIOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        url = (
            f"{self.endpoint}/openai/deployments/"
            f"{self.deployment_name}/chat/completions"
            f"?api-version={self.api_version}"
        )
        config: Dict[str, Any] = {
            "url": url,
            "api_key": self.api_key,
            "vendor": self.vendor or "azure",
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }

        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if params:
            config["params"] = params
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class AnthropicOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(..., description="Model name")
    url: str = Field(..., description="Anthropic messages endpoint URL")
    max_tokens: int = Field(..., gt=0)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Dict[str, str] = Field(..., description="Anthropic request headers")
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")


class Anthropic(AnthropicOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.url,
            "api_key": self.api_key,
            "params": params,
            "headers": self.headers,
            "style": "anthropic",
            "input_modalities": self.input_modalities or ["text"],
        }

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class GeminiOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Google AI API key")
    model: str = Field(..., description="Model name")
    url: Optional[str] = Field(default=None, description="Custom API endpoint URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, gt=0)
    max_output_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")


class Gemini(GeminiOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.top_k is not None:
            params["top_k"] = self.top_k
        if self.max_output_tokens is not None:
            params["max_output_tokens"] = self.max_output_tokens

        config: Dict[str, Any] = {
            "url": self.url or (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
            ),
            "params": params,
            "style": "gemini",
            "input_modalities": self.input_modalities or ["text"],
        }

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.headers is not None:
            config["headers"] = self.headers
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class GroqOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Groq API key")
    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="Groq-compatible endpoint")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "GroqOptions":
        if not self.model:
            raise ValueError("Groq requires model")
        return self


class Groq(GroqOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url,
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        return config


class CustomLLMOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Custom LLM API key")
    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="OpenAI-compatible chat completions endpoint")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")

    @model_validator(mode="after")
    def _validate_byok_params(self) -> "CustomLLMOptions":
        if not self.model:
            raise ValueError("CustomLLM requires model")
        return self


class CustomLLM(CustomLLMOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.api_key is not None:
            config["api_key"] = self.api_key
        if self.headers is not None:
            config["headers"] = self.headers

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        config["vendor"] = self.vendor or "custom"
        return config


class VertexAILLMOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Vertex AI access token or API key")
    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(..., description="Google Cloud location")
    model: str = Field(..., description="Model name")
    url: Optional[str] = Field(default=None, description="Custom API endpoint URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, gt=0)
    max_output_tokens: Optional[int] = Field(default=None, gt=0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")


class VertexAILLM(VertexAILLMOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.top_k is not None:
            params["top_k"] = self.top_k
        if self.max_output_tokens is not None:
            params["max_output_tokens"] = self.max_output_tokens

        url = self.url or (
            f"https://{self.location}-aiplatform.googleapis.com/v1/projects/"
            f"{self.project_id}/locations/{self.location}/"
            f"publishers/google/models/{self.model}:streamGenerateContent?alt=sse"
        )

        config: Dict[str, Any] = {
            "url": url,
            "params": params,
            "style": "gemini",
            "input_modalities": self.input_modalities or ["text"],
        }

        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.headers is not None:
            config["headers"] = self.headers
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history

        config["api_key"] = self.api_key
        return config


class AmazonBedrockOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_key: str = Field(..., description="AWS access key ID")
    secret_key: str = Field(..., description="AWS secret access key")
    region: str = Field(..., description="AWS region")
    model: str = Field(..., description="Amazon Bedrock model identifier")
    max_tokens: Optional[int] = Field(default=None, gt=0)
    url: Optional[str] = Field(default=None, description="Amazon Bedrock converse stream endpoint URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0, description="Maximum number of conversation history messages to cache")


class AmazonBedrock(AmazonBedrockOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.params or {})
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.top_p is not None:
            params["top_p"] = self.top_p

        config: Dict[str, Any] = {
            "url": self.url or f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model}/converse-stream",
            "access_key": self.access_key,
            "secret_key": self.secret_key,
            "region": self.region,
            "model": self.model,
            "params": params,
            "style": "bedrock",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.headers is not None:
            config["headers"] = self.headers
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history
        return config


class DifyOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Dify API key")
    url: str = Field(..., description="Dify workflow or chat endpoint")
    model: str = Field(..., description="Dify model identifier")
    user: Optional[str] = Field(default=None, description="Dify user identifier")
    conversation_id: Optional[str] = Field(default=None, description="Dify conversation ID")
    system_messages: Optional[List[Dict[str, Any]]] = Field(default=None)
    greeting_message: Optional[str] = Field(default=None)
    greeting_audio_url: Optional[str] = Field(default=None)
    failure_message: Optional[str] = Field(default=None)
    input_modalities: Optional[List[str]] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None)
    headers: Optional[Dict[str, str]] = Field(default=None)
    output_modalities: Optional[List[str]] = Field(default=None)
    greeting_configs: Optional[LlmGreetingConfigs] = Field(default=None)
    template_variables: Optional[Dict[str, str]] = Field(default=None)
    vendor: Optional[str] = Field(default=None)
    mcp_servers: Optional[List[Dict[str, Any]]] = Field(default=None)
    max_history: Optional[int] = Field(default=None, gt=0)


class Dify(DifyOptions, BaseLLM):
    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.model, **(self.params or {})}
        if self.user is not None:
            params["user"] = self.user
        if self.conversation_id is not None:
            params["conversation_id"] = self.conversation_id

        config: Dict[str, Any] = {
            "url": self.url,
            "api_key": self.api_key,
            "params": params,
            "style": "dify",
            "input_modalities": self.input_modalities or ["text"],
        }
        if self.headers is not None:
            config["headers"] = self.headers
        if self.system_messages is not None:
            config["system_messages"] = self.system_messages
        if self.greeting_message is not None:
            config["greeting_message"] = self.greeting_message
        if self.greeting_audio_url is not None:
            config["greeting_audio_url"] = self.greeting_audio_url
        if self.failure_message is not None:
            config["failure_message"] = self.failure_message
        if self.output_modalities is not None:
            config["output_modalities"] = self.output_modalities
        if self.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.greeting_configs)
        if self.template_variables is not None:
            config["template_variables"] = self.template_variables
        if self.vendor is not None:
            config["vendor"] = self.vendor
        if self.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.mcp_servers)
        if self.max_history is not None:
            config["max_history"] = self.max_history
        return config
