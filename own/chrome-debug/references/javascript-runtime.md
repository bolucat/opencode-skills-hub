# JavaScript Runtime Debugging

Use this reference for runtime state, browser APIs, event handlers, and JavaScript behavior.

## Evaluate script

Use `evaluate_script` only when the required information is not available through:

- console
- network
- snapshot
- source code

Good uses:

- inspect a specific runtime value
- check a specific DOM property
- inspect browser API state
- verify event-related state
- query a narrowly scoped element

Bad uses:

- dumping the entire DOM
- serializing the entire window object
- dumping localStorage
- dumping cookies
- dumping global variables
- returning large application state

## Keep evaluations narrow

Prefer:

```javascript
document.querySelector('[data-testid="login"]')?.disabled
```

over:

```javascript
document.documentElement.outerHTML
```

Prefer:

```javascript
window.location.href
```

over dumping `window`.

## Event debugging

When a UI event fails:

1. inspect console
2. locate source handler
3. inspect DOM state
4. inspect runtime state only if needed
5. inspect network request if the event triggers one

Do not modify runtime state permanently unless explicitly requested.

## Async problems

Check:

- Promise rejection
- missing await
- race conditions
- stale closures
- component lifecycle
- request cancellation
- state updates after unmount

## Browser APIs

For browser-specific behavior investigate:

- localStorage
- sessionStorage
- IndexedDB
- service workers
- WebSocket
- Web Workers

Only inspect the minimum required data.

Never dump credentials or sensitive storage values.