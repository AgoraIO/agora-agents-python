from __future__ import annotations

from typing import Dict, List, Optional, Union

from ._transport import _UNSET, AsyncResource, RawResponse, Resource, segment
from .types import (
    AgentCreateModel_AudioGreeting,
    AgentCreateModel_CascadedPipeline,
    AgentCreateModel_FillerWords,
    AgentCreateModel_Message,
    AgentCreateModel_RealtimePipeline,
    AgentCreateModel_TextGreeting,
    AgentCreateModel_VariableDefinition,
    AgentDeleteResponse,
    AgentListResponse,
    AgentPatchRequest_FillerWordsPatch,
    AgentPatchRequest_GreetingPatch,
    AgentPatchRequest_Message,
    AgentPatchRequest_PipelinePatch,
    AgentPatchRequest_VariableDefinitionPatch,
    AgentResponse,
    InboundInput,
    NumberDeleteResponse,
    NumberListResponse,
    NumberResponse,
    SecretDeleted,
    SecretKey,
    SecretList,
    SecretSet,
    SessionList,
    SessionResponse,
    SipTrunkInput,
)
from typing_extensions import Literal


class AgentsClient(Resource):
    with_raw_response: AgentsRawClient

    def create(self, *, appid: Optional[str] = None, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentCreateModel_Message'], None] = _UNSET, greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None] = _UNSET, variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None] = _UNSET, pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None] = _UNSET, filler_words: Union['AgentCreateModel_FillerWords', None] = _UNSET, request_options: Optional[dict] = None) -> 'AgentResponse':
        return self.with_raw_response.create(appid=appid, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, request_options=request_options).data

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> 'AgentListResponse':
        return self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options).data

    def get(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> 'AgentResponse':
        return self.with_raw_response.get(appid=appid, agent_id=agent_id, request_options=request_options).data

    def update(self, *, appid: Optional[str] = None, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentPatchRequest_Message'], None] = _UNSET, greeting: Union['AgentPatchRequest_GreetingPatch', None] = _UNSET, variables: Union[Dict[str, Union['AgentPatchRequest_VariableDefinitionPatch', None]], None] = _UNSET, pipeline: Union['AgentPatchRequest_PipelinePatch', None] = _UNSET, filler_words: Union['AgentPatchRequest_FillerWordsPatch', None] = _UNSET, request_options: Optional[dict] = None) -> 'AgentResponse':
        return self.with_raw_response.update(appid=appid, agent_id=agent_id, if_match=if_match, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, request_options=request_options).data

    def delete(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> 'AgentDeleteResponse':
        return self.with_raw_response.delete(appid=appid, agent_id=agent_id, request_options=request_options).data


class AgentsRawClient(Resource):
    def create(self, *, appid: Optional[str] = None, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentCreateModel_Message'], None] = _UNSET, greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None] = _UNSET, variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None] = _UNSET, pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None] = _UNSET, filler_words: Union['AgentCreateModel_FillerWords', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={}, params={}, request_options=request_options)

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, appid: Optional[str] = None, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentPatchRequest_Message'], None] = _UNSET, greeting: Union['AgentPatchRequest_GreetingPatch', None] = _UNSET, variables: Union[Dict[str, Union['AgentPatchRequest_VariableDefinitionPatch', None]], None] = _UNSET, pipeline: Union['AgentPatchRequest_PipelinePatch', None] = _UNSET, filler_words: Union['AgentPatchRequest_FillerWordsPatch', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

def _AgentsClient(owner, options):
    client = AgentsClient(owner, options)
    client.with_raw_response = AgentsRawClient(owner, options)
    return client

class SecretsClient(Resource):
    with_raw_response: SecretsRawClient

    def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, name: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> 'SecretSet':
        return self.with_raw_response.create(appid=appid, idempotency_key=idempotency_key, name=name, secrets=secrets, request_options=request_options).data

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, request_options: Optional[dict] = None) -> 'SecretList':
        return self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options).data

    def get(self, *, appid: Optional[str] = None, name: str, request_options: Optional[dict] = None) -> 'SecretSet':
        return self.with_raw_response.get(appid=appid, name=name, request_options=request_options).data

    def replace(self, *, appid: Optional[str] = None, name: str, if_match: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> 'SecretSet':
        return self.with_raw_response.replace(appid=appid, name=name, if_match=if_match, secrets=secrets, request_options=request_options).data

    def update(self, *, appid: Optional[str] = None, name: str, if_match: Optional[str] = None, secrets: Dict[str, Union[str, None]], request_options: Optional[dict] = None) -> 'SecretSet':
        return self.with_raw_response.update(appid=appid, name=name, if_match=if_match, secrets=secrets, request_options=request_options).data

    def delete(self, *, appid: Optional[str] = None, name: str, if_match: str, request_options: Optional[dict] = None) -> 'SecretDeleted':
        return self.with_raw_response.delete(appid=appid, name=name, if_match=if_match, request_options=request_options).data

    def set_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, if_none_match: Optional[str] = None, value: str, request_options: Optional[dict] = None) -> 'SecretKey':
        return self.with_raw_response.set_key(appid=appid, name=name, key=key, if_match=if_match, if_none_match=if_none_match, value=value, request_options=request_options).data

    def delete_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, request_options: Optional[dict] = None) -> 'SecretDeleted':
        return self.with_raw_response.delete_key(appid=appid, name=name, key=key, if_match=if_match, request_options=request_options).data


class SecretsRawClient(Resource):
    def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, name: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> RawResponse:
        return self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body={'name': name, 'secrets': secrets}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, appid: Optional[str] = None, name: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={}, params={}, request_options=request_options)

    def replace(self, *, appid: Optional[str] = None, name: str, if_match: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> RawResponse:
        return self._request('PUT', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def update(self, *, appid: Optional[str] = None, name: str, if_match: Optional[str] = None, secrets: Dict[str, Union[str, None]], request_options: Optional[dict] = None) -> RawResponse:
        return self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, appid: Optional[str] = None, name: str, if_match: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def set_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, if_none_match: Optional[str] = None, value: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('PUT', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body={'value': value}, headers={'If-Match': if_match, 'If-None-Match': if_none_match}, params={}, request_options=request_options)

    def delete_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

def _SecretsClient(owner, options):
    client = SecretsClient(owner, options)
    client.with_raw_response = SecretsRawClient(owner, options)
    return client

class NumbersClient(Resource):
    with_raw_response: NumbersRawClient

    def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, number: str, description: Union[str, None] = _UNSET, sip_trunk: 'SipTrunkInput', inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> 'NumberResponse':
        return self.with_raw_response.create(appid=appid, idempotency_key=idempotency_key, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, request_options=request_options).data

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> 'NumberListResponse':
        return self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options).data

    def get(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> 'NumberResponse':
        return self.with_raw_response.get(appid=appid, number_id=number_id, request_options=request_options).data

    def update(self, *, appid: Optional[str] = None, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union['SipTrunkInput', None] = _UNSET, inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> 'NumberResponse':
        return self.with_raw_response.update(appid=appid, number_id=number_id, if_match=if_match, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, request_options=request_options).data

    def delete(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> 'NumberDeleteResponse':
        return self.with_raw_response.delete(appid=appid, number_id=number_id, request_options=request_options).data


class NumbersRawClient(Resource):
    def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, number: str, description: Union[str, None] = _UNSET, sip_trunk: 'SipTrunkInput', inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, appid: Optional[str] = None, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union['SipTrunkInput', None] = _UNSET, inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

def _NumbersClient(owner, options):
    client = NumbersClient(owner, options)
    client.with_raw_response = NumbersRawClient(owner, options)
    return client

class SessionsClient(Resource):
    with_raw_response: SessionsRawClient

    def list(self, *, appid: Optional[str] = None, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, request_options: Optional[dict] = None) -> 'SessionList':
        return self.with_raw_response.list(appid=appid, channel=channel, status=status, started_after=started_after, started_before=started_before, limit=limit, cursor=cursor, request_options=request_options).data

    def get(self, *, appid: Optional[str] = None, agent_session_id: str, request_options: Optional[dict] = None) -> 'SessionResponse':
        return self.with_raw_response.get(appid=appid, agent_session_id=agent_session_id, request_options=request_options).data


class SessionsRawClient(Resource):
    def list(self, *, appid: Optional[str] = None, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body=None, headers={}, params={'channel': channel, 'status': status, 'started_after': started_after, 'started_before': started_before, 'limit': limit, 'cursor': cursor}, request_options=request_options)

    def get(self, *, appid: Optional[str] = None, agent_session_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body=None, headers={}, params={}, request_options=request_options)

def _SessionsClient(owner, options):
    client = SessionsClient(owner, options)
    client.with_raw_response = SessionsRawClient(owner, options)
    return client

class V3Client:
    def __init__(self, owner, options):
        self.agents = _AgentsClient(owner, options)
        self.secrets = _SecretsClient(owner, options)
        self.numbers = _NumbersClient(owner, options)
        self.sessions = _SessionsClient(owner, options)

class AsyncAgentsClient(AsyncResource):
    with_raw_response: AsyncAgentsRawClient

    async def create(self, *, appid: Optional[str] = None, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentCreateModel_Message'], None] = _UNSET, greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None] = _UNSET, variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None] = _UNSET, pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None] = _UNSET, filler_words: Union['AgentCreateModel_FillerWords', None] = _UNSET, request_options: Optional[dict] = None) -> 'AgentResponse':
        return (await self.with_raw_response.create(appid=appid, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, request_options=request_options)).data

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> 'AgentListResponse':
        return (await self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options)).data

    async def get(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> 'AgentResponse':
        return (await self.with_raw_response.get(appid=appid, agent_id=agent_id, request_options=request_options)).data

    async def update(self, *, appid: Optional[str] = None, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentPatchRequest_Message'], None] = _UNSET, greeting: Union['AgentPatchRequest_GreetingPatch', None] = _UNSET, variables: Union[Dict[str, Union['AgentPatchRequest_VariableDefinitionPatch', None]], None] = _UNSET, pipeline: Union['AgentPatchRequest_PipelinePatch', None] = _UNSET, filler_words: Union['AgentPatchRequest_FillerWordsPatch', None] = _UNSET, request_options: Optional[dict] = None) -> 'AgentResponse':
        return (await self.with_raw_response.update(appid=appid, agent_id=agent_id, if_match=if_match, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, request_options=request_options)).data

    async def delete(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> 'AgentDeleteResponse':
        return (await self.with_raw_response.delete(appid=appid, agent_id=agent_id, request_options=request_options)).data


class AsyncAgentsRawClient(AsyncResource):
    async def create(self, *, appid: Optional[str] = None, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentCreateModel_Message'], None] = _UNSET, greeting: Union[Union['AgentCreateModel_TextGreeting', 'AgentCreateModel_AudioGreeting'], None] = _UNSET, variables: Union[Dict[str, 'AgentCreateModel_VariableDefinition'], None] = _UNSET, pipeline: Union[Union['AgentCreateModel_CascadedPipeline', 'AgentCreateModel_RealtimePipeline'], None] = _UNSET, filler_words: Union['AgentCreateModel_FillerWords', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={}, params={}, request_options=request_options)

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, appid: Optional[str] = None, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List['AgentPatchRequest_Message'], None] = _UNSET, greeting: Union['AgentPatchRequest_GreetingPatch', None] = _UNSET, variables: Union[Dict[str, Union['AgentPatchRequest_VariableDefinitionPatch', None]], None] = _UNSET, pipeline: Union['AgentPatchRequest_PipelinePatch', None] = _UNSET, filler_words: Union['AgentPatchRequest_FillerWordsPatch', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, appid: Optional[str] = None, agent_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

def _AsyncAgentsClient(owner, options):
    client = AsyncAgentsClient(owner, options)
    client.with_raw_response = AsyncAgentsRawClient(owner, options)
    return client

class AsyncSecretsClient(AsyncResource):
    with_raw_response: AsyncSecretsRawClient

    async def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, name: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> 'SecretSet':
        return (await self.with_raw_response.create(appid=appid, idempotency_key=idempotency_key, name=name, secrets=secrets, request_options=request_options)).data

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, request_options: Optional[dict] = None) -> 'SecretList':
        return (await self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options)).data

    async def get(self, *, appid: Optional[str] = None, name: str, request_options: Optional[dict] = None) -> 'SecretSet':
        return (await self.with_raw_response.get(appid=appid, name=name, request_options=request_options)).data

    async def replace(self, *, appid: Optional[str] = None, name: str, if_match: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> 'SecretSet':
        return (await self.with_raw_response.replace(appid=appid, name=name, if_match=if_match, secrets=secrets, request_options=request_options)).data

    async def update(self, *, appid: Optional[str] = None, name: str, if_match: Optional[str] = None, secrets: Dict[str, Union[str, None]], request_options: Optional[dict] = None) -> 'SecretSet':
        return (await self.with_raw_response.update(appid=appid, name=name, if_match=if_match, secrets=secrets, request_options=request_options)).data

    async def delete(self, *, appid: Optional[str] = None, name: str, if_match: str, request_options: Optional[dict] = None) -> 'SecretDeleted':
        return (await self.with_raw_response.delete(appid=appid, name=name, if_match=if_match, request_options=request_options)).data

    async def set_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, if_none_match: Optional[str] = None, value: str, request_options: Optional[dict] = None) -> 'SecretKey':
        return (await self.with_raw_response.set_key(appid=appid, name=name, key=key, if_match=if_match, if_none_match=if_none_match, value=value, request_options=request_options)).data

    async def delete_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, request_options: Optional[dict] = None) -> 'SecretDeleted':
        return (await self.with_raw_response.delete_key(appid=appid, name=name, key=key, if_match=if_match, request_options=request_options)).data


class AsyncSecretsRawClient(AsyncResource):
    async def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, name: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body={'name': name, 'secrets': secrets}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, appid: Optional[str] = None, name: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={}, params={}, request_options=request_options)

    async def replace(self, *, appid: Optional[str] = None, name: str, if_match: str, secrets: Dict[str, str], request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('PUT', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def update(self, *, appid: Optional[str] = None, name: str, if_match: Optional[str] = None, secrets: Dict[str, Union[str, None]], request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, appid: Optional[str] = None, name: str, if_match: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def set_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, if_none_match: Optional[str] = None, value: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('PUT', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body={'value': value}, headers={'If-Match': if_match, 'If-None-Match': if_none_match}, params={}, request_options=request_options)

    async def delete_key(self, *, appid: Optional[str] = None, name: str, key: str, if_match: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

def _AsyncSecretsClient(owner, options):
    client = AsyncSecretsClient(owner, options)
    client.with_raw_response = AsyncSecretsRawClient(owner, options)
    return client

class AsyncNumbersClient(AsyncResource):
    with_raw_response: AsyncNumbersRawClient

    async def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, number: str, description: Union[str, None] = _UNSET, sip_trunk: 'SipTrunkInput', inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> 'NumberResponse':
        return (await self.with_raw_response.create(appid=appid, idempotency_key=idempotency_key, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, request_options=request_options)).data

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> 'NumberListResponse':
        return (await self.with_raw_response.list(appid=appid, limit=limit, cursor=cursor, order=order, request_options=request_options)).data

    async def get(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> 'NumberResponse':
        return (await self.with_raw_response.get(appid=appid, number_id=number_id, request_options=request_options)).data

    async def update(self, *, appid: Optional[str] = None, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union['SipTrunkInput', None] = _UNSET, inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> 'NumberResponse':
        return (await self.with_raw_response.update(appid=appid, number_id=number_id, if_match=if_match, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, request_options=request_options)).data

    async def delete(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> 'NumberDeleteResponse':
        return (await self.with_raw_response.delete(appid=appid, number_id=number_id, request_options=request_options)).data


class AsyncNumbersRawClient(AsyncResource):
    async def create(self, *, appid: Optional[str] = None, idempotency_key: Optional[str] = None, number: str, description: Union[str, None] = _UNSET, sip_trunk: 'SipTrunkInput', inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('POST', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def list(self, *, appid: Optional[str] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, appid: Optional[str] = None, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union['SipTrunkInput', None] = _UNSET, inbound: Union['InboundInput', None] = _UNSET, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('PATCH', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, appid: Optional[str] = None, number_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('DELETE', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

def _AsyncNumbersClient(owner, options):
    client = AsyncNumbersClient(owner, options)
    client.with_raw_response = AsyncNumbersRawClient(owner, options)
    return client

class AsyncSessionsClient(AsyncResource):
    with_raw_response: AsyncSessionsRawClient

    async def list(self, *, appid: Optional[str] = None, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, request_options: Optional[dict] = None) -> 'SessionList':
        return (await self.with_raw_response.list(appid=appid, channel=channel, status=status, started_after=started_after, started_before=started_before, limit=limit, cursor=cursor, request_options=request_options)).data

    async def get(self, *, appid: Optional[str] = None, agent_session_id: str, request_options: Optional[dict] = None) -> 'SessionResponse':
        return (await self.with_raw_response.get(appid=appid, agent_session_id=agent_session_id, request_options=request_options)).data


class AsyncSessionsRawClient(AsyncResource):
    async def list(self, *, appid: Optional[str] = None, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body=None, headers={}, params={'channel': channel, 'status': status, 'started_after': started_after, 'started_before': started_before, 'limit': limit, 'cursor': cursor}, request_options=request_options)

    async def get(self, *, appid: Optional[str] = None, agent_session_id: str, request_options: Optional[dict] = None) -> RawResponse:
        return await self._request('GET', f'/conversational-ai/v3/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body=None, headers={}, params={}, request_options=request_options)

def _AsyncSessionsClient(owner, options):
    client = AsyncSessionsClient(owner, options)
    client.with_raw_response = AsyncSessionsRawClient(owner, options)
    return client

class AsyncV3Client:
    def __init__(self, owner, options):
        self.agents = _AsyncAgentsClient(owner, options)
        self.secrets = _AsyncSecretsClient(owner, options)
        self.numbers = _AsyncNumbersClient(owner, options)
        self.sessions = _AsyncSessionsClient(owner, options)
