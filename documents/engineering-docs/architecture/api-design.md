# API Design Guidelines — Acme Corp

**Owner:** Architecture Review Board
**Last Updated:** 2024-11-05
**Applies To:** All public and internal REST APIs

---

## REST Conventions

All Acme APIs follow RESTful resource-oriented design. URLs represent resources (nouns), and HTTP methods represent actions (verbs).

### URL Structure

```
https://api.acme.io/v{version}/{resource}/{id}/{sub-resource}
```

### HTTP Methods

| Method | Usage | Idempotent | Example |
|--------|-------|------------|---------|
| `GET` | Retrieve a resource or collection | Yes | `GET /v2/users/123` |
| `POST` | Create a new resource | No | `POST /v2/users` |
| `PUT` | Full replacement of a resource | Yes | `PUT /v2/users/123` |
| `PATCH` | Partial update of a resource | Yes | `PATCH /v2/users/123` |
| `DELETE` | Remove a resource | Yes | `DELETE /v2/users/123` |

### Naming Rules

- Use lowercase kebab-case for URL segments: `/user-profiles`, not `/userProfiles`.
- Use plural nouns for collections: `/users`, `/invoices`, `/projects`.
- Avoid deeply nested resources (max 2 levels): `/projects/456/tasks` is acceptable; `/projects/456/tasks/789/comments/12` is not — use `/task-comments/12` instead.

---

## Versioning Strategy

- API versions are included in the URL path: `/v1/`, `/v2/`, etc.
- Major versions increment when breaking changes are introduced (field removal, type changes, behavioral changes).
- Minor and non-breaking changes (new optional fields, new endpoints) do not require a version bump.
- **Deprecation policy:** A deprecated API version is supported for 12 months after the successor version reaches GA. Deprecation notices are communicated via the `Sunset` HTTP header and the developer changelog.

### Current Versions

| Version | Status | Sunset Date |
|---------|--------|-------------|
| v1 | Deprecated | 2025-06-30 |
| v2 | Stable (current) | — |
| v3 | Beta (internal only) | — |

---

## Authentication

### OAuth2 (User Context)

- All user-facing API calls require a Bearer token issued by `acme-auth`.
- Token format: JWT signed with RS256, 1-hour expiry, refreshable via `/v2/auth/refresh`.
- Scopes control access granularity: `read:users`, `write:billing`, `admin:tenants`, etc.

### API Keys (Service Context)

- Machine-to-machine integrations use API keys passed via the `X-API-Key` header.
- API keys are scoped to a tenant and a set of permissions.
- Keys are generated in the Acme Dashboard under Settings > API Keys.
- Keys can be rotated without downtime; the previous key remains valid for 24 hours after rotation.

### Authentication Flow

```
Client → Kong Gateway (validates token/key)
       → Injects X-Tenant-ID and X-User-ID headers
       → Forwards to downstream service
```

Services must never trust client-supplied tenant or user identity. Always read from gateway-injected headers.

---

## Rate Limiting

Rate limits are enforced at the Kong API Gateway layer.

| Plan | Requests/min | Burst | Concurrent |
|------|-------------|-------|------------|
| Free | 60 | 10 | 5 |
| Starter | 300 | 50 | 20 |
| Business | 1,200 | 200 | 50 |
| Enterprise | 6,000 | 1,000 | 200 |

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 1200
X-RateLimit-Remaining: 1147
X-RateLimit-Reset: 1701234567
```

When the limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header.

---

## Error Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body contains invalid fields.",
    "details": [
      {
        "field": "email",
        "reason": "Must be a valid email address.",
        "value": "not-an-email"
      }
    ],
    "request_id": "req_abc123def456",
    "documentation_url": "https://docs.acme.io/errors/VALIDATION_ERROR"
  }
}
```

### Standard Error Codes

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| 400 | `VALIDATION_ERROR` | Request body or parameters are invalid |
| 401 | `AUTHENTICATION_REQUIRED` | Missing or expired token/key |
| 403 | `FORBIDDEN` | Valid credentials but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist or is not accessible |
| 409 | `CONFLICT` | Resource state conflict (e.g., duplicate email) |
| 422 | `UNPROCESSABLE_ENTITY` | Semantically invalid request |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error (include request_id in bug reports) |

---

## Pagination

All collection endpoints support cursor-based pagination.

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 25 | Items per page (max 100) |
| `cursor` | string | — | Opaque cursor from previous response |
| `sort` | string | `created_at` | Field to sort by |
| `order` | string | `desc` | Sort direction (`asc` or `desc`) |

### Response Envelope

```json
{
  "data": [ ... ],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNH0=",
    "has_more": true,
    "total_count": 1842
  }
}
```

- `total_count` is only included when the query cost is acceptable (collections under 100k records). For larger collections, it is omitted.
- Clients must not construct cursors manually; they are opaque and may change format.

---

## Request/Response Standards

- **Content-Type:** `application/json` for all request and response bodies.
- **Date format:** ISO 8601 with timezone (`2024-11-05T14:30:00Z`).
- **ID format:** UUIDv4 for all resource identifiers.
- **Null handling:** Omit null fields from responses rather than sending `"field": null`.
- **Envelope:** All successful responses are wrapped in a `"data"` key. Single resources return `"data": { ... }`, collections return `"data": [ ... ]`.

---

## Documentation Requirements

Every API endpoint must include:

1. **OpenAPI 3.1 specification** in the `api-specs` repository, kept in sync with implementation.
2. **Inline docstrings** in the FastAPI route handler describing purpose, parameters, and error cases.
3. **Changelog entry** in `docs/api-changelog.md` for any new or modified endpoint.
4. **Example requests and responses** in the OpenAPI spec using the `examples` keyword.
5. **Rate limit documentation** specifying which plan tiers have access to the endpoint.

API specs are automatically published to `https://docs.acme.io/api` on every merge to main.
