# Console Debugging

Use this reference for JavaScript runtime errors and browser console problems.

## First action

Inspect console messages before doing broad browser exploration.

Focus on:

- errors
- uncaught exceptions
- rejected promises
- framework runtime errors
- warnings directly related to the reported behavior

Ignore unrelated warnings unless they provide evidence for the problem.

## Error prioritization

Prefer:

1. Uncaught exceptions
2. Errors occurring immediately before the failure
3. Errors with source-mapped stack traces
4. Failed module/resource errors
5. Relevant framework errors
6. Warnings

Do not assume the first console message is the root cause.

## Stack traces

When a stack trace exists:

1. Identify the application source file.
2. Identify the function.
3. Identify the line.
4. Search the local project.
5. Inspect the relevant code.

Prefer source files over generated bundles.

## Common patterns

### `Cannot read properties of undefined`

Check:

- initialization order
- async state
- optional data
- API response shape
- component lifecycle
- race conditions

### `is not a function`

Check:

- import/export mismatch
- incorrect object shape
- stale API
- wrong module version
- method name

### `Failed to fetch`

Check:

- request URL
- server availability
- CORS
- protocol
- network request details

### `ChunkLoadError`

Check:

- deployment version mismatch
- stale browser cache
- missing chunk
- service worker
- CDN/cache behavior

### Framework-specific errors

Do not immediately assume the framework is broken.

Trace the error back to application code whenever possible.

## After fixing

Always reproduce the original action.

A console becoming quiet is not sufficient if the original functionality still fails.