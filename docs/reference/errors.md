---
sidebar_position: 5
title: Error Responses
description: Error handling notes for Conversational AI API responses.
---

# Error Responses

API v2.7 updates the error status codes and `reason` values surfaced through the generated client.

## Status Codes

In addition to existing validation and task errors, integrations should handle:

- `401` — authentication failed
- `429` — rate limit exceeded
- `500` — internal server error

## Reason Migration

If your application branches on `AgentErrorResponse.reason`, update handlers for the v2.7 reasons:

| Previous | v2.7 replacements |
|---|---|
| `InvalidRequest` | `InvalidRequestBody`, `MissingRequiredField`, `InvalidFieldValue` |

New reasons include `ServiceNotEnabled`, `AccountSuspended`, and `ResourceAllocationFailed`.

Prefer treating unknown reasons as retryable only when the HTTP status and operation are safe to retry.
