# DOM and UI Debugging

Use this reference for DOM structure, accessibility, element interaction, layout, and UI behavior.

## Preferred inspection order

1. Snapshot
2. Targeted DOM inspection
3. JavaScript evaluation if necessary
4. Screenshot for visual issues

Prefer text/accessibility information over screenshots for non-visual problems.

## Snapshot

Use snapshots to understand:

- page structure
- accessible names
- buttons
- links
- forms
- inputs
- visible content

Do not request repeated full snapshots unless the page changed substantially.

## Element identification

Prefer stable identifiers:

1. semantic role
2. accessible name
3. id
4. data-testid
5. stable class
6. CSS selector

Avoid fragile selectors based on generated class names.

## Click problems

If a click does not work, check:

- element exists
- element is visible
- element is enabled
- overlay is blocking it
- event handler is attached
- JavaScript error occurs
- application state prevents the action

Do not repeatedly click the same element without inspecting why it failed.

## Form problems

Check:

- input value
- validation
- disabled state
- submit handler
- network request
- error message

## Visual problems

Use screenshots for:

- layout
- spacing
- colors
- responsive behavior
- overlapping elements
- typography

Do not use screenshots for ordinary JavaScript debugging.

## Responsive debugging

When debugging responsive layout:

1. identify target viewport
2. reproduce at that viewport
3. inspect screenshot
4. locate relevant CSS
5. modify source
6. reproduce

Avoid testing many viewport sizes unless requested.

## Framework applications

For React/Vue/etc.:

Prefer source code and application state over manipulating the live DOM directly.

Do not use `evaluate_script` to permanently modify the page as a substitute for editing source code.