# Chrome Debugging Workflow

Use this reference when the problem type is unclear or when multiple browser debugging techniques may apply.

## Decision tree

### JavaScript error

Symptoms:

- page throws an exception
- button stops working
- blank page
- component fails to render
- console shows red errors

Workflow:

1. Inspect console messages.
2. Find the first meaningful error.
3. Follow the stack trace.
4. Locate the original source file.
5. Inspect surrounding code.
6. Fix the source.
7. Reload/reproduce.
8. Verify the console.

Do not start with screenshots or performance tracing.

---

### API/network problem

Symptoms:

- HTTP 4xx/5xx
- request never completes
- wrong response
- CORS error
- request payload appears incorrect
- UI shows stale server data

Workflow:

1. Identify the request.
2. Check URL and method.
3. Check status.
4. Check request payload.
5. Check response.
6. Compare with frontend source.
7. Inspect backend source if necessary.
8. Fix.
9. Reproduce.

---

### UI problem

Symptoms:

- element missing
- wrong text
- button cannot be found
- click does not work
- wrong element receives interaction

Workflow:

1. Use a snapshot.
2. Locate the element.
3. Inspect only the relevant DOM region.
4. Check application state/event handler.
5. Use screenshot only if appearance is relevant.

---

### Visual problem

Symptoms:

- wrong spacing
- broken layout
- wrong color
- incorrect responsive behavior
- overlapping elements

Workflow:

1. Inspect viewport.
2. Take screenshot.
3. Identify visual difference.
4. Inspect relevant DOM/CSS source.
5. Modify source.
6. Reload.
7. Screenshot again only if necessary.

---

### Performance problem

Symptoms:

- slow initial load
- slow interaction
- jank
- high CPU usage
- layout shifts

Workflow:

1. Establish the exact performance symptom.
2. Start a trace.
3. Reproduce the problem.
4. Stop the trace.
5. Inspect the relevant insight.
6. Identify source code responsible.
7. Fix.
8. Re-test.

Never start performance tracing for an ordinary runtime error.