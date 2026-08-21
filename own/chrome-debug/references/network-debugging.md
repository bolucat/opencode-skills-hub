# Network Debugging

Use this reference for API, HTTP, CORS, loading, authentication, and frontend/backend communication problems.

## Minimal inspection

Start with:

1. Request URL
2. HTTP method
3. Status code
4. Request timing if relevant

Only inspect payload/response when necessary.

## Request filtering

When many requests exist:

- identify the feature being debugged
- identify the likely API
- narrow by URL or request behavior
- inspect only relevant requests

Do not dump the entire network log.

## Status codes

### 400

Check:

- request payload
- required fields
- content type
- validation

### 401

Check:

- authentication state
- authorization header
- cookie/session
- token expiration

Never copy sensitive authentication tokens into chat or source files.

### 403

Check:

- permissions
- CSRF
- origin
- authorization rules

### 404

Check:

- URL
- API version
- routing
- frontend environment configuration

### 409

Check:

- duplicate resources
- optimistic concurrency
- state conflicts

### 422

Check:

- validation errors
- request schema

### 429

Check:

- rate limits
- retry behavior
- request frequency

### 500

Inspect the response only when useful, then investigate the backend.

Do not repeatedly retry a failing production endpoint.

## CORS

If the browser reports CORS:

Check:

1. Request origin
2. Target origin
3. Preflight request
4. Response `Access-Control-Allow-*` headers
5. Backend configuration

Do not attempt to "fix CORS" by disabling browser security.

Fix the server configuration or development proxy.

## Authentication

Never expose:

- cookies
- session tokens
- bearer tokens
- API keys
- passwords

If authentication data is visible in a request, reason about it without reproducing the secret in output.

## Request/response bodies

Only inspect bodies when needed.

Prefer:

- status
- headers relevant to the issue
- small JSON fields

Avoid returning huge responses into the model context.

## Verification

After changing code:

1. reproduce the request
2. confirm status
3. confirm relevant response
4. verify UI behavior
5. run appropriate local tests