"""Generated resources from root openapi.json; shared token transport is handwritten."""
from __future__ import annotations

from typing import Dict, List, Optional, Union

from . import types as T
from ._transport import _UNSET, AsyncResource, RawResponse, Resource, segment
from typing_extensions import Literal


class AgentsClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AgentsRawClient(owner, options)
    def create(self, *, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[Union[T.AgentRequest_TextGreeting, T.AgentRequest_AudioGreeting], None] = _UNSET, variables: Union[Dict[str, T.AgentRequest_VariableDefinition], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelineInput, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWords, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return self.with_raw_response.create(agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, appid=appid, request_options=request_options).data

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentListResponse:
        return self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options).data

    def get(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return self.with_raw_response.get(agent_id=agent_id, appid=appid, request_options=request_options).data

    def update(self, *, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[T.AgentRequest_GreetingPatch, None] = _UNSET, variables: Union[Dict[str, Union[T.AgentRequest_VariableDefinitionPatch, None]], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelinePatch, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWordsPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return self.with_raw_response.update(agent_id=agent_id, if_match=if_match, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, appid=appid, request_options=request_options).data

    def delete(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentDeleteResponse:
        return self.with_raw_response.delete(agent_id=agent_id, appid=appid, request_options=request_options).data

class AgentsRawClient(Resource):
    def create(self, *, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[Union[T.AgentRequest_TextGreeting, T.AgentRequest_AudioGreeting], None] = _UNSET, variables: Union[Dict[str, T.AgentRequest_VariableDefinition], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelineInput, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWords, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={}, params={}, request_options=request_options)

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentListResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[T.AgentRequest_GreetingPatch, None] = _UNSET, variables: Union[Dict[str, Union[T.AgentRequest_VariableDefinitionPatch, None]], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelinePatch, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWordsPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentDeleteResponse]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

class SecretsClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = SecretsRawClient(owner, options)
    def create(self, *, name: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return self.with_raw_response.create(name=name, secrets=secrets, appid=appid, request_options=request_options).data

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretList:
        return self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options).data

    def get(self, *, name: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return self.with_raw_response.get(name=name, appid=appid, request_options=request_options).data

    def replace(self, *, name: str, if_match: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return self.with_raw_response.replace(name=name, if_match=if_match, secrets=secrets, appid=appid, request_options=request_options).data

    def update(self, *, name: str, if_match: Optional[Union[str, None]] = None, secrets: Dict[str, Union[str, None]], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return self.with_raw_response.update(name=name, if_match=if_match, secrets=secrets, appid=appid, request_options=request_options).data

    def delete(self, *, name: str, if_match: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretDeleted:
        return self.with_raw_response.delete(name=name, if_match=if_match, appid=appid, request_options=request_options).data

    def set_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, if_none_match: Optional[Union[Literal['*'], None]] = None, value: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretKey:
        return self.with_raw_response.set_key(name=name, key=key, if_match=if_match, if_none_match=if_none_match, value=value, appid=appid, request_options=request_options).data

    def delete_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretDeleted:
        return self.with_raw_response.delete_key(name=name, key=key, if_match=if_match, appid=appid, request_options=request_options).data

class SecretsRawClient(Resource):
    def create(self, *, name: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body={'name': name, 'secrets': secrets}, headers={}, params={}, request_options=request_options)

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretList]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, name: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={}, params={}, request_options=request_options)

    def replace(self, *, name: str, if_match: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return self._request('PUT', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def update(self, *, name: str, if_match: Optional[Union[str, None]] = None, secrets: Dict[str, Union[str, None]], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, name: str, if_match: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretDeleted]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def set_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, if_none_match: Optional[Union[Literal['*'], None]] = None, value: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretKey]:
        return self._request('PUT', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body={'value': value}, headers={'If-Match': if_match, 'If-None-Match': if_none_match}, params={}, request_options=request_options)

    def delete_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretDeleted]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

class NumbersClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = NumbersRawClient(owner, options)
    def create(self, *, number: str, description: Union[str, None] = _UNSET, sip_trunk: T.SipTrunkInput, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return self.with_raw_response.create(number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, appid=appid, request_options=request_options).data

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberListResponse:
        return self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options).data

    def get(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return self.with_raw_response.get(number_id=number_id, appid=appid, request_options=request_options).data

    def update(self, *, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union[T.SipTrunkInput, None] = _UNSET, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return self.with_raw_response.update(number_id=number_id, if_match=if_match, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, appid=appid, request_options=request_options).data

    def delete(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberDeleteResponse:
        return self.with_raw_response.delete(number_id=number_id, appid=appid, request_options=request_options).data

class NumbersRawClient(Resource):
    def create(self, *, number: str, description: Union[str, None] = _UNSET, sip_trunk: T.SipTrunkInput, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={}, params={}, request_options=request_options)

    def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberListResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union[T.SipTrunkInput, None] = _UNSET, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberDeleteResponse]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

class SessionsClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = SessionsRawClient(owner, options)
    def start(self, *, idempotency_key: Optional[str] = None, agent_id: str, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStartResponse:
        return self.with_raw_response.start(idempotency_key=idempotency_key, agent_id=agent_id, values=values, labels=labels, transport=transport, lifecycle=lifecycle, data_policy=data_policy, appid=appid, request_options=request_options).data

    def list(self, *, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionList:
        return self.with_raw_response.list(channel=channel, status=status, started_after=started_after, started_before=started_before, limit=limit, cursor=cursor, appid=appid, request_options=request_options).data

    def start_ephemeral(self, *, idempotency_key: Optional[str] = None, agent: T.PublicAgentInput, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStartResponse:
        return self.with_raw_response.start_ephemeral(idempotency_key=idempotency_key, agent=agent, values=values, labels=labels, transport=transport, lifecycle=lifecycle, data_policy=data_policy, appid=appid, request_options=request_options).data

    def get(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionResponse:
        return self.with_raw_response.get(agent_session_id=agent_session_id, appid=appid, request_options=request_options).data

    def update(self, *, agent_session_id: str, transport: T.SessionTransportPatch = _UNSET, agent: T.SessionAgentPatch = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionUpdateResponse:
        return self.with_raw_response.update(agent_session_id=agent_session_id, transport=transport, agent=agent, appid=appid, request_options=request_options).data

    def stop(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStopResponse:
        return self.with_raw_response.stop(agent_session_id=agent_session_id, appid=appid, request_options=request_options).data

class SessionsRawClient(Resource):
    def start(self, *, idempotency_key: Optional[str] = None, agent_id: str, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStartResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body={'agent_id': agent_id, 'values': values, 'labels': labels, 'transport': transport, 'lifecycle': lifecycle, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def list(self, *, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionList]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body=None, headers={}, params={'channel': channel, 'status': status, 'started_after': started_after, 'started_before': started_before, 'limit': limit, 'cursor': cursor}, request_options=request_options)

    def start_ephemeral(self, *, idempotency_key: Optional[str] = None, agent: T.PublicAgentInput, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStartResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/ephemeral', body={'agent': agent, 'values': values, 'labels': labels, 'transport': transport, 'lifecycle': lifecycle, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def get(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, agent_session_id: str, transport: T.SessionTransportPatch = _UNSET, agent: T.SessionAgentPatch = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionUpdateResponse]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body={'transport': transport, 'agent': agent}, headers={}, params={}, request_options=request_options)

    def stop(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStopResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}/stop', body=None, headers={}, params={}, request_options=request_options)

class CampaignsClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = CampaignsRawClient(owner, options)
    def create(self, *, idempotency_key: Optional[str] = None, name: str, agent_id: str, transport: T.CampaignTransport, contacts: List[T.ContactInput], lifecycle: T.CampaignLifecycle = _UNSET, pacing: T.Pacing = _UNSET, schedule: Union[T.ImmediateSchedule, T.ScheduledSchedule], data_policy: T.DataPolicy = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.create(idempotency_key=idempotency_key, name=name, agent_id=agent_id, transport=transport, contacts=contacts, lifecycle=lifecycle, pacing=pacing, schedule=schedule, data_policy=data_policy, appid=appid, request_options=request_options).data

    def list(self, *, status: Optional[Union[Literal['scheduled', 'running', 'paused', 'completed', 'canceled', 'failed'], None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignListResponse:
        return self.with_raw_response.list(status=status, limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options).data

    def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.pause(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.resume(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.cancel(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.get(campaign_id=campaign_id, appid=appid, request_options=request_options).data

    def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[T.CampaignLifecycle, None] = _UNSET, pacing: Union[T.PacingPatch, None] = _UNSET, schedule: Union[Union[T.ImmediateSchedule, T.ScheduledSchedule], None] = _UNSET, transport: Union[T.CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return self.with_raw_response.update(campaign_id=campaign_id, if_match=if_match, lifecycle=lifecycle, pacing=pacing, schedule=schedule, transport=transport, appid=appid, request_options=request_options).data

    def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignDeleteResponse:
        return self.with_raw_response.delete(campaign_id=campaign_id, appid=appid, request_options=request_options).data

class CampaignsRawClient(Resource):
    def create(self, *, idempotency_key: Optional[str] = None, name: str, agent_id: str, transport: T.CampaignTransport, contacts: List[T.ContactInput], lifecycle: T.CampaignLifecycle = _UNSET, pacing: T.Pacing = _UNSET, schedule: Union[T.ImmediateSchedule, T.ScheduledSchedule], data_policy: T.DataPolicy = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body={'name': name, 'agent_id': agent_id, 'transport': transport, 'contacts': contacts, 'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def list(self, *, status: Optional[Union[Literal['scheduled', 'running', 'paused', 'completed', 'canceled', 'failed'], None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignListResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body=None, headers={}, params={'status': status, 'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:pause', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:resume', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:cancel', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[T.CampaignLifecycle, None] = _UNSET, pacing: Union[T.PacingPatch, None] = _UNSET, schedule: Union[Union[T.ImmediateSchedule, T.ScheduledSchedule], None] = _UNSET, transport: Union[T.CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body={'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'transport': transport}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignDeleteResponse]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

class V3Client:
    def __init__(self, owner, options):
        self.agents = AgentsClient(owner, options)
        self.secrets = SecretsClient(owner, options)
        self.numbers = NumbersClient(owner, options)
        self.sessions = SessionsClient(owner, options)
        self.campaigns = CampaignsClient(owner, options)

class AsyncAgentsClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncAgentsRawClient(owner, options)
    async def create(self, *, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[Union[T.AgentRequest_TextGreeting, T.AgentRequest_AudioGreeting], None] = _UNSET, variables: Union[Dict[str, T.AgentRequest_VariableDefinition], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelineInput, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWords, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return (await self.with_raw_response.create(agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, appid=appid, request_options=request_options)).data

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentListResponse:
        return (await self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options)).data

    async def get(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return (await self.with_raw_response.get(agent_id=agent_id, appid=appid, request_options=request_options)).data

    async def update(self, *, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[T.AgentRequest_GreetingPatch, None] = _UNSET, variables: Union[Dict[str, Union[T.AgentRequest_VariableDefinitionPatch, None]], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelinePatch, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWordsPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentResponse:
        return (await self.with_raw_response.update(agent_id=agent_id, if_match=if_match, agent_name=agent_name, instructions=instructions, messages=messages, greeting=greeting, variables=variables, pipeline=pipeline, filler_words=filler_words, appid=appid, request_options=request_options)).data

    async def delete(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.AgentDeleteResponse:
        return (await self.with_raw_response.delete(agent_id=agent_id, appid=appid, request_options=request_options)).data

class AsyncAgentsRawClient(AsyncResource):
    async def create(self, *, agent_name: str, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[Union[T.AgentRequest_TextGreeting, T.AgentRequest_AudioGreeting], None] = _UNSET, variables: Union[Dict[str, T.AgentRequest_VariableDefinition], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelineInput, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWords, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={}, params={}, request_options=request_options)

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentListResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, agent_id: str, if_match: str, agent_name: Union[str, None] = _UNSET, instructions: Union[str, None] = _UNSET, messages: Union[List[T.AgentRequest_Message], None] = _UNSET, greeting: Union[T.AgentRequest_GreetingPatch, None] = _UNSET, variables: Union[Dict[str, Union[T.AgentRequest_VariableDefinitionPatch, None]], None] = _UNSET, pipeline: Union[T.AgentRequest_CascadedPipelinePatch, None] = _UNSET, filler_words: Union[T.AgentRequest_FillerWordsPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentResponse]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body={'agent_name': agent_name, 'instructions': instructions, 'messages': messages, 'greeting': greeting, 'variables': variables, 'pipeline': pipeline, 'filler_words': filler_words}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, agent_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.AgentDeleteResponse]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/agents/{segment(agent_id)}', body=None, headers={}, params={}, request_options=request_options)

class AsyncSecretsClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncSecretsRawClient(owner, options)
    async def create(self, *, name: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return (await self.with_raw_response.create(name=name, secrets=secrets, appid=appid, request_options=request_options)).data

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretList:
        return (await self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options)).data

    async def get(self, *, name: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return (await self.with_raw_response.get(name=name, appid=appid, request_options=request_options)).data

    async def replace(self, *, name: str, if_match: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return (await self.with_raw_response.replace(name=name, if_match=if_match, secrets=secrets, appid=appid, request_options=request_options)).data

    async def update(self, *, name: str, if_match: Optional[Union[str, None]] = None, secrets: Dict[str, Union[str, None]], appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretSet:
        return (await self.with_raw_response.update(name=name, if_match=if_match, secrets=secrets, appid=appid, request_options=request_options)).data

    async def delete(self, *, name: str, if_match: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretDeleted:
        return (await self.with_raw_response.delete(name=name, if_match=if_match, appid=appid, request_options=request_options)).data

    async def set_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, if_none_match: Optional[Union[Literal['*'], None]] = None, value: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretKey:
        return (await self.with_raw_response.set_key(name=name, key=key, if_match=if_match, if_none_match=if_none_match, value=value, appid=appid, request_options=request_options)).data

    async def delete_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SecretDeleted:
        return (await self.with_raw_response.delete_key(name=name, key=key, if_match=if_match, appid=appid, request_options=request_options)).data

class AsyncSecretsRawClient(AsyncResource):
    async def create(self, *, name: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body={'name': name, 'secrets': secrets}, headers={}, params={}, request_options=request_options)

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.asc', 'create_ts.desc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretList]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, name: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={}, params={}, request_options=request_options)

    async def replace(self, *, name: str, if_match: str, secrets: Dict[str, str], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return await self._request('PUT', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def update(self, *, name: str, if_match: Optional[Union[str, None]] = None, secrets: Dict[str, Union[str, None]], appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretSet]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body={'secrets': secrets}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, name: str, if_match: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretDeleted]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def set_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, if_none_match: Optional[Union[Literal['*'], None]] = None, value: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretKey]:
        return await self._request('PUT', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body={'value': value}, headers={'If-Match': if_match, 'If-None-Match': if_none_match}, params={}, request_options=request_options)

    async def delete_key(self, *, name: str, key: str, if_match: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SecretDeleted]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/secrets/{segment(name)}/keys/{segment(key)}', body=None, headers={'If-Match': if_match}, params={}, request_options=request_options)

class AsyncNumbersClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncNumbersRawClient(owner, options)
    async def create(self, *, number: str, description: Union[str, None] = _UNSET, sip_trunk: T.SipTrunkInput, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return (await self.with_raw_response.create(number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, appid=appid, request_options=request_options)).data

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberListResponse:
        return (await self.with_raw_response.list(limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options)).data

    async def get(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return (await self.with_raw_response.get(number_id=number_id, appid=appid, request_options=request_options)).data

    async def update(self, *, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union[T.SipTrunkInput, None] = _UNSET, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberResponse:
        return (await self.with_raw_response.update(number_id=number_id, if_match=if_match, number=number, description=description, sip_trunk=sip_trunk, inbound=inbound, appid=appid, request_options=request_options)).data

    async def delete(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.NumberDeleteResponse:
        return (await self.with_raw_response.delete(number_id=number_id, appid=appid, request_options=request_options)).data

class AsyncNumbersRawClient(AsyncResource):
    async def create(self, *, number: str, description: Union[str, None] = _UNSET, sip_trunk: T.SipTrunkInput, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={}, params={}, request_options=request_options)

    async def list(self, *, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberListResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers', body=None, headers={}, params={'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, number_id: str, if_match: str, number: Union[str, None] = _UNSET, description: Union[str, None] = _UNSET, sip_trunk: Union[T.SipTrunkInput, None] = _UNSET, inbound: Union[T.InboundInput, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberResponse]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body={'number': number, 'description': description, 'sip_trunk': sip_trunk, 'inbound': inbound}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, number_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.NumberDeleteResponse]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/numbers/{segment(number_id)}', body=None, headers={}, params={}, request_options=request_options)

class AsyncSessionsClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncSessionsRawClient(owner, options)
    async def start(self, *, idempotency_key: Optional[str] = None, agent_id: str, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStartResponse:
        return (await self.with_raw_response.start(idempotency_key=idempotency_key, agent_id=agent_id, values=values, labels=labels, transport=transport, lifecycle=lifecycle, data_policy=data_policy, appid=appid, request_options=request_options)).data

    async def list(self, *, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionList:
        return (await self.with_raw_response.list(channel=channel, status=status, started_after=started_after, started_before=started_before, limit=limit, cursor=cursor, appid=appid, request_options=request_options)).data

    async def start_ephemeral(self, *, idempotency_key: Optional[str] = None, agent: T.PublicAgentInput, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStartResponse:
        return (await self.with_raw_response.start_ephemeral(idempotency_key=idempotency_key, agent=agent, values=values, labels=labels, transport=transport, lifecycle=lifecycle, data_policy=data_policy, appid=appid, request_options=request_options)).data

    async def get(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionResponse:
        return (await self.with_raw_response.get(agent_session_id=agent_session_id, appid=appid, request_options=request_options)).data

    async def update(self, *, agent_session_id: str, transport: T.SessionTransportPatch = _UNSET, agent: T.SessionAgentPatch = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionUpdateResponse:
        return (await self.with_raw_response.update(agent_session_id=agent_session_id, transport=transport, agent=agent, appid=appid, request_options=request_options)).data

    async def stop(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.SessionStopResponse:
        return (await self.with_raw_response.stop(agent_session_id=agent_session_id, appid=appid, request_options=request_options)).data

class AsyncSessionsRawClient(AsyncResource):
    async def start(self, *, idempotency_key: Optional[str] = None, agent_id: str, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStartResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body={'agent_id': agent_id, 'values': values, 'labels': labels, 'transport': transport, 'lifecycle': lifecycle, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def list(self, *, channel: Optional[Union[str, None]] = None, status: Optional[str] = None, started_after: Optional[Union[int, None]] = None, started_before: Optional[Union[int, None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionList]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions', body=None, headers={}, params={'channel': channel, 'status': status, 'started_after': started_after, 'started_before': started_before, 'limit': limit, 'cursor': cursor}, request_options=request_options)

    async def start_ephemeral(self, *, idempotency_key: Optional[str] = None, agent: T.PublicAgentInput, values: Union[Dict[str, Union[str, int, float, bool]], None] = _UNSET, labels: Union[Dict[str, str], None] = _UNSET, transport: T.SessionTransport, lifecycle: Union[T.Lifecycle, None] = _UNSET, data_policy: Union[T.DataPolicy, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStartResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/ephemeral', body={'agent': agent, 'values': values, 'labels': labels, 'transport': transport, 'lifecycle': lifecycle, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def get(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, agent_session_id: str, transport: T.SessionTransportPatch = _UNSET, agent: T.SessionAgentPatch = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionUpdateResponse]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}', body={'transport': transport, 'agent': agent}, headers={}, params={}, request_options=request_options)

    async def stop(self, *, agent_session_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.SessionStopResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/sessions/{segment(agent_session_id)}/stop', body=None, headers={}, params={}, request_options=request_options)

class AsyncCampaignsClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncCampaignsRawClient(owner, options)
    async def create(self, *, idempotency_key: Optional[str] = None, name: str, agent_id: str, transport: T.CampaignTransport, contacts: List[T.ContactInput], lifecycle: T.CampaignLifecycle = _UNSET, pacing: T.Pacing = _UNSET, schedule: Union[T.ImmediateSchedule, T.ScheduledSchedule], data_policy: T.DataPolicy = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.create(idempotency_key=idempotency_key, name=name, agent_id=agent_id, transport=transport, contacts=contacts, lifecycle=lifecycle, pacing=pacing, schedule=schedule, data_policy=data_policy, appid=appid, request_options=request_options)).data

    async def list(self, *, status: Optional[Union[Literal['scheduled', 'running', 'paused', 'completed', 'canceled', 'failed'], None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignListResponse:
        return (await self.with_raw_response.list(status=status, limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options)).data

    async def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.pause(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.resume(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.cancel(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.get(campaign_id=campaign_id, appid=appid, request_options=request_options)).data

    async def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[T.CampaignLifecycle, None] = _UNSET, pacing: Union[T.PacingPatch, None] = _UNSET, schedule: Union[Union[T.ImmediateSchedule, T.ScheduledSchedule], None] = _UNSET, transport: Union[T.CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignResponse:
        return (await self.with_raw_response.update(campaign_id=campaign_id, if_match=if_match, lifecycle=lifecycle, pacing=pacing, schedule=schedule, transport=transport, appid=appid, request_options=request_options)).data

    async def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> T.CampaignDeleteResponse:
        return (await self.with_raw_response.delete(campaign_id=campaign_id, appid=appid, request_options=request_options)).data

class AsyncCampaignsRawClient(AsyncResource):
    async def create(self, *, idempotency_key: Optional[str] = None, name: str, agent_id: str, transport: T.CampaignTransport, contacts: List[T.ContactInput], lifecycle: T.CampaignLifecycle = _UNSET, pacing: T.Pacing = _UNSET, schedule: Union[T.ImmediateSchedule, T.ScheduledSchedule], data_policy: T.DataPolicy = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body={'name': name, 'agent_id': agent_id, 'transport': transport, 'contacts': contacts, 'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'data_policy': data_policy}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def list(self, *, status: Optional[Union[Literal['scheduled', 'running', 'paused', 'completed', 'canceled', 'failed'], None]] = None, limit: Optional[int] = None, cursor: Optional[Union[str, None]] = None, order: Optional[Literal['create_ts.desc', 'create_ts.asc']] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignListResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body=None, headers={}, params={'status': status, 'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:pause', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:resume', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:cancel', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[T.CampaignLifecycle, None] = _UNSET, pacing: Union[T.PacingPatch, None] = _UNSET, schedule: Union[Union[T.ImmediateSchedule, T.ScheduledSchedule], None] = _UNSET, transport: Union[T.CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignResponse]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body={'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'transport': transport}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[T.CampaignDeleteResponse]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

class AsyncV3Client:
    def __init__(self, owner, options):
        self.agents = AsyncAgentsClient(owner, options)
        self.secrets = AsyncSecretsClient(owner, options)
        self.numbers = AsyncNumbersClient(owner, options)
        self.sessions = AsyncSessionsClient(owner, options)
        self.campaigns = AsyncCampaignsClient(owner, options)
