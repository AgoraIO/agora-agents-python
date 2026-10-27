"""Typed campaign operations; lifecycle semantics follow the engineering reply."""
from __future__ import annotations

from typing import List, Optional, Union

from ._transport import _UNSET, AsyncResource, RawResponse, Resource, segment
from .types import (
    CampaignDeleteResponse,
    CampaignLifecycle,
    CampaignListResponse,
    CampaignResponse,
    CampaignTransport,
    CampaignTransportPatch,
    ContactInput,
    ImmediateSchedule,
    Pacing,
    PacingPatch,
    ScheduledSchedule,
)
from typing_extensions import Literal


class CampaignsClient(Resource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = CampaignsRawClient(owner, options)

    def create(self, *, name: str, agent_id: str, transport: CampaignTransport, contacts: List[ContactInput], schedule: Union[ImmediateSchedule, ScheduledSchedule], lifecycle: Optional[CampaignLifecycle] = None, pacing: Optional[Pacing] = None, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.create(name=name, agent_id=agent_id, transport=transport, contacts=contacts, schedule=schedule, lifecycle=lifecycle, pacing=pacing, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def list(self, *, status: Optional[Literal["scheduled", "running", "paused", "completed", "canceled", "failed"]] = None, limit: Optional[int] = None, cursor: Optional[str] = None, order: Optional[Literal["create_ts.asc", "create_ts.desc"]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignListResponse:
        return self.with_raw_response.list(status=status, limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options).data

    def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.get(campaign_id=campaign_id, appid=appid, request_options=request_options).data

    def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[CampaignLifecycle, None] = _UNSET, pacing: Union[PacingPatch, None] = _UNSET, schedule: Union[ImmediateSchedule, ScheduledSchedule, None] = _UNSET, transport: Union[CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.update(campaign_id=campaign_id, if_match=if_match, lifecycle=lifecycle, pacing=pacing, schedule=schedule, transport=transport, appid=appid, request_options=request_options).data

    def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignDeleteResponse:
        return self.with_raw_response.delete(campaign_id=campaign_id, appid=appid, request_options=request_options).data

    def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.pause(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.resume(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data

    def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return self.with_raw_response.cancel(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options).data


class CampaignsRawClient(Resource):

    def create(self, *, name: str, agent_id: str, transport: CampaignTransport, contacts: List[ContactInput], schedule: Union[ImmediateSchedule, ScheduledSchedule], lifecycle: Optional[CampaignLifecycle] = None, pacing: Optional[Pacing] = None, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body={k: v for k, v in {'name': name, 'agent_id': agent_id, 'transport': transport, 'contacts': contacts, 'schedule': schedule, 'lifecycle': lifecycle, 'pacing': pacing}.items() if v is not None}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def list(self, *, status: Optional[Literal["scheduled", "running", "paused", "completed", "canceled", "failed"]] = None, limit: Optional[int] = None, cursor: Optional[str] = None, order: Optional[Literal["create_ts.asc", "create_ts.desc"]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignListResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body=None, headers={}, params={'status': status, 'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[CampaignLifecycle, None] = _UNSET, pacing: Union[PacingPatch, None] = _UNSET, schedule: Union[ImmediateSchedule, ScheduledSchedule, None] = _UNSET, transport: Union[CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body={'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'transport': transport}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignDeleteResponse]:
        return self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:pause', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:resume', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:cancel', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)


class AsyncCampaignsClient(AsyncResource):
    def __init__(self, owner, options):
        super().__init__(owner, options)
        self.with_raw_response = AsyncCampaignsRawClient(owner, options)

    async def create(self, *, name: str, agent_id: str, transport: CampaignTransport, contacts: List[ContactInput], schedule: Union[ImmediateSchedule, ScheduledSchedule], lifecycle: Optional[CampaignLifecycle] = None, pacing: Optional[Pacing] = None, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.create(name=name, agent_id=agent_id, transport=transport, contacts=contacts, schedule=schedule, lifecycle=lifecycle, pacing=pacing, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def list(self, *, status: Optional[Literal["scheduled", "running", "paused", "completed", "canceled", "failed"]] = None, limit: Optional[int] = None, cursor: Optional[str] = None, order: Optional[Literal["create_ts.asc", "create_ts.desc"]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignListResponse:
        return (await self.with_raw_response.list(status=status, limit=limit, cursor=cursor, order=order, appid=appid, request_options=request_options)).data

    async def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.get(campaign_id=campaign_id, appid=appid, request_options=request_options)).data

    async def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[CampaignLifecycle, None] = _UNSET, pacing: Union[PacingPatch, None] = _UNSET, schedule: Union[ImmediateSchedule, ScheduledSchedule, None] = _UNSET, transport: Union[CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.update(campaign_id=campaign_id, if_match=if_match, lifecycle=lifecycle, pacing=pacing, schedule=schedule, transport=transport, appid=appid, request_options=request_options)).data

    async def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignDeleteResponse:
        return (await self.with_raw_response.delete(campaign_id=campaign_id, appid=appid, request_options=request_options)).data

    async def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.pause(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.resume(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data

    async def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> CampaignResponse:
        return (await self.with_raw_response.cancel(campaign_id=campaign_id, idempotency_key=idempotency_key, appid=appid, request_options=request_options)).data


class AsyncCampaignsRawClient(AsyncResource):

    async def create(self, *, name: str, agent_id: str, transport: CampaignTransport, contacts: List[ContactInput], schedule: Union[ImmediateSchedule, ScheduledSchedule], lifecycle: Optional[CampaignLifecycle] = None, pacing: Optional[Pacing] = None, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body={k: v for k, v in {'name': name, 'agent_id': agent_id, 'transport': transport, 'contacts': contacts, 'schedule': schedule, 'lifecycle': lifecycle, 'pacing': pacing}.items() if v is not None}, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def list(self, *, status: Optional[Literal["scheduled", "running", "paused", "completed", "canceled", "failed"]] = None, limit: Optional[int] = None, cursor: Optional[str] = None, order: Optional[Literal["create_ts.asc", "create_ts.desc"]] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignListResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns', body=None, headers={}, params={'status': status, 'limit': limit, 'cursor': cursor, 'order': order}, request_options=request_options)

    async def get(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('GET', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def update(self, *, campaign_id: str, if_match: str, lifecycle: Union[CampaignLifecycle, None] = _UNSET, pacing: Union[PacingPatch, None] = _UNSET, schedule: Union[ImmediateSchedule, ScheduledSchedule, None] = _UNSET, transport: Union[CampaignTransportPatch, None] = _UNSET, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('PATCH', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body={'lifecycle': lifecycle, 'pacing': pacing, 'schedule': schedule, 'transport': transport}, headers={'If-Match': if_match}, params={}, request_options=request_options)

    async def delete(self, *, campaign_id: str, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignDeleteResponse]:
        return await self._request('DELETE', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}', body=None, headers={}, params={}, request_options=request_options)

    async def pause(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:pause', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def resume(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:resume', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)

    async def cancel(self, *, campaign_id: str, idempotency_key: Optional[str] = None, appid: Optional[str] = None, request_options: Optional[dict] = None) -> RawResponse[CampaignResponse]:
        return await self._request('POST', f'/conversational-ai/v1/projects/{segment(self.owner.app_id if appid is None else appid)}/campaigns/{segment(campaign_id)}:cancel', body=None, headers={'Idempotency-Key': idempotency_key}, params={}, request_options=request_options)
