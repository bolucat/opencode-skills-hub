# Token Efficiency

The purpose of this reference is to minimize unnecessary browser context.

## General principle

Do not optimize for the fewest tool calls.

Optimize for the smallest useful amount of information returned to the model.

One precise request is better than five broad requests.

## Preferred information hierarchy

Use this order whenever possible:

1. Local source code
2. Console error
3. Stack trace
4. Targeted network request
5. Targeted DOM/snapshot
6. Runtime evaluation
7. Screenshot
8. Performance trace

The later an item appears, the more selectively it should be used.

## Console

Bad:

- retrieve all console messages repeatedly

Good:

- retrieve relevant errors
- identify the first meaningful failure
- follow its stack trace

## Network

Bad:

- list every request
- inspect every response

Good:

- identify the relevant request
- inspect only its details

## DOM

Bad:

```text
full page DOM
```

Good:

```text
relevant subtree
```

## Screenshot

Use screenshots only when visual information is necessary.

Avoid screenshots for:

- JavaScript errors
- API failures
- state bugs
- event handler problems

## evaluate_script

Never dump:

- `window`
- `document`
- `localStorage`
- `sessionStorage`
- cookies
- IndexedDB
- complete application state

Use narrow expressions.

## Repeated operations

If a tool returned enough information to answer the current question, do not call it again.

## Large outputs

If a tool returns too much data:

1. do not repeat the same request
2. narrow the query
3. inspect a specific item
4. save large artifacts to files when supported

## Browser tabs

Do not inspect unrelated tabs.

## Performance

Do not collect traces unless performance is the problem.

## Final response

Do not include a transcript of browser tool calls.

Return:

- root cause
- changed files
- verification
- remaining issue