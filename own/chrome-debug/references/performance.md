# Performance Debugging

Use this reference only for actual performance investigations.

## Before tracing

Define the symptom:

- slow load
- slow interaction
- long task
- rendering jank
- layout shift
- excessive JavaScript
- slow network
- memory growth

Do not trace without a concrete question.

## Trace workflow

1. Navigate to the correct page.
2. Establish the reproduction steps.
3. Start a performance trace.
4. Reproduce the problem.
5. Stop the trace.
6. Inspect relevant performance insights.
7. Identify source code.
8. Make a targeted fix.
9. Re-test.

## Core Web Vitals

### LCP

Investigate:

- largest content resource
- image loading
- server response
- render blocking
- client-side rendering

### INP

Investigate:

- long JavaScript tasks
- event handlers
- rendering work
- synchronous computation

### CLS

Investigate:

- images without dimensions
- dynamically inserted content
- font loading
- layout changes

## Long tasks

Look for:

- expensive loops
- large JSON processing
- synchronous computation
- excessive DOM work
- unnecessary rendering

## Network performance

Check:

- request count
- payload size
- blocking resources
- caching
- waterfall

Do not inspect every request if one request clearly explains the problem.

## Memory

Only perform heap/memory investigations when there is evidence of memory growth or leaks.

Memory snapshots can be very large. Save them to a file when possible instead of returning huge data directly to the model.

## Token efficiency

Performance traces can produce large amounts of information.

Always analyze the relevant insight first.

Do not repeatedly request the complete trace.