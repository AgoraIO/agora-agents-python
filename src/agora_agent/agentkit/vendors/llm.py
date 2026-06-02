from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import BaseLLM

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

class OpenAI(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = OpenAIOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        # model is the default; explicit params entries extend/override it.
        # This matches the TS SDK behaviour: { model, ...params }.
        params: Dict[str, Any] = {"model": self.options.model, **(self.options.params or {})}

        # Named fields take precedence over anything in the generic params dict.
        if self.options.max_tokens is not None:
            params["max_tokens"] = self.options.max_tokens
        if self.options.temperature is not None:
            params["temperature"] = self.options.temperature
        if self.options.top_p is not None:
            params["top_p"] = self.options.top_p

        config: Dict[str, Any] = {
            "url": self.options.base_url or "https://api.openai.com/v1/chat/completions",
            "params": params,
            "style": "openai",
            "input_modalities": self.options.input_modalities or ["text"],
        }
        if self.options.api_key is not None:
            config["api_key"] = self.options.api_key
        if self.options.headers is not None:
            config["headers"] = self.options.headers

        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.vendor is not None:
            config["vendor"] = self.options.vendor
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history

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

class AzureOpenAI(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = AzureOpenAIOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        url = (
            f"{self.options.endpoint}/openai/deployments/"
            f"{self.options.deployment_name}/chat/completions"
            f"?api-version={self.options.api_version}"
        )
        config: Dict[str, Any] = {
            "url": url,
            "api_key": self.options.api_key,
            "vendor": self.options.vendor or "azure",
            "style": "openai",
            "input_modalities": self.options.input_modalities or ["text"],
        }

        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.options.model, **(self.options.params or {})}
        if self.options.temperature is not None:
            params["temperature"] = self.options.temperature
        if self.options.top_p is not None:
            params["top_p"] = self.options.top_p
        if self.options.max_tokens is not None:
            params["max_tokens"] = self.options.max_tokens
        if params:
            config["params"] = params
        if self.options.headers is not None:
            config["headers"] = self.options.headers

        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history

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

class Anthropic(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = AnthropicOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.options.model, **(self.options.params or {})}
        if self.options.max_tokens is not None:
            params["max_tokens"] = self.options.max_tokens
        if self.options.temperature is not None:
            params["temperature"] = self.options.temperature
        if self.options.top_p is not None:
            params["top_p"] = self.options.top_p

        config: Dict[str, Any] = {
            "url": self.options.url,
            "api_key": self.options.api_key,
            "params": params,
            "headers": self.options.headers,
            "style": "anthropic",
            "input_modalities": self.options.input_modalities or ["text"],
        }

        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.vendor is not None:
            config["vendor"] = self.options.vendor
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history

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

class Gemini(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = GeminiOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        # Named fields take precedence over anything in the generic params dict.
        params: Dict[str, Any] = {"model": self.options.model, **(self.options.params or {})}
        if self.options.temperature is not None:
            params["temperature"] = self.options.temperature
        if self.options.top_p is not None:
            params["top_p"] = self.options.top_p
        if self.options.top_k is not None:
            params["top_k"] = self.options.top_k
        if self.options.max_output_tokens is not None:
            params["max_output_tokens"] = self.options.max_output_tokens

        config: Dict[str, Any] = {
            "url": self.options.url or "https://generativelanguage.googleapis.com/v1beta/models",
            "api_key": self.options.api_key,
            "params": params,
            "style": "gemini",
            "input_modalities": self.options.input_modalities or ["text"],
        }

        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.headers is not None:
            config["headers"] = self.options.headers
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.vendor is not None:
            config["vendor"] = self.options.vendor
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history

        return config


class GroqOptions(OpenAIOptions):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Groq API key")
    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="Groq-compatible endpoint")


class Groq(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = GroqOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        config = OpenAI(**_dump_optional_model(self.options)).to_config()
        config["url"] = self.options.base_url
        return config


class CustomLLMOptions(OpenAIOptions):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Custom LLM API key")
    base_url: str = Field(..., description="OpenAI-compatible chat completions endpoint")


class CustomLLM(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = CustomLLMOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        config = OpenAI(**_dump_optional_model(self.options)).to_config()
        config["vendor"] = self.options.vendor or "custom"
        return config


class VertexAILLMOptions(GeminiOptions):
    model_config = ConfigDict(extra="forbid")

    api_key: str = Field(..., description="Vertex AI access token or API key")
    project_id: str = Field(..., description="Google Cloud project ID")
    location: str = Field(..., description="Google Cloud location")


class VertexAILLM(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = VertexAILLMOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        options = _dump_optional_model(self.options)
        options.pop("project_id", None)
        options.pop("location", None)
        config = Gemini(**options).to_config()
        params = dict(config["params"])
        params["project_id"] = self.options.project_id
        params["location"] = self.options.location
        config["params"] = params
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


class AmazonBedrock(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = AmazonBedrockOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = dict(self.options.params or {})
        if self.options.max_tokens is not None:
            params["max_tokens"] = self.options.max_tokens
        if self.options.temperature is not None:
            params["temperature"] = self.options.temperature
        if self.options.top_p is not None:
            params["top_p"] = self.options.top_p

        config: Dict[str, Any] = {
            "url": self.options.url or f"https://bedrock-runtime.{self.options.region}.amazonaws.com/model/{self.options.model}/converse-stream",
            "access_key": self.options.access_key,
            "secret_key": self.options.secret_key,
            "region": self.options.region,
            "model": self.options.model,
            "params": params,
            "style": "bedrock",
            "input_modalities": self.options.input_modalities or ["text"],
        }
        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.headers is not None:
            config["headers"] = self.options.headers
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.vendor is not None:
            config["vendor"] = self.options.vendor
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history
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


class Dify(BaseLLM):
    def __init__(self, **kwargs: Any):
        self.options = DifyOptions(**kwargs)

    def to_config(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"model": self.options.model, **(self.options.params or {})}
        if self.options.user is not None:
            params["user"] = self.options.user
        if self.options.conversation_id is not None:
            params["conversation_id"] = self.options.conversation_id

        config: Dict[str, Any] = {
            "url": self.options.url,
            "api_key": self.options.api_key,
            "params": params,
            "style": "dify",
            "input_modalities": self.options.input_modalities or ["text"],
        }
        if self.options.headers is not None:
            config["headers"] = self.options.headers
        if self.options.system_messages is not None:
            config["system_messages"] = self.options.system_messages
        if self.options.greeting_message is not None:
            config["greeting_message"] = self.options.greeting_message
        if self.options.failure_message is not None:
            config["failure_message"] = self.options.failure_message
        if self.options.output_modalities is not None:
            config["output_modalities"] = self.options.output_modalities
        if self.options.greeting_configs is not None:
            config["greeting_configs"] = _dump_optional_model(self.options.greeting_configs)
        if self.options.template_variables is not None:
            config["template_variables"] = self.options.template_variables
        if self.options.vendor is not None:
            config["vendor"] = self.options.vendor
        if self.options.mcp_servers is not None:
            config["mcp_servers"] = _ensure_mcp_transport(self.options.mcp_servers)
        if self.options.max_history is not None:
            config["max_history"] = self.options.max_history
        return config
