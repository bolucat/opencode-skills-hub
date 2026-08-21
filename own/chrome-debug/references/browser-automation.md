# Browser Automation

Use this reference when the task requires interacting with a webpage.

## General rule

Automation should be purposeful.

Do not browse randomly.

## Page selection

Before interacting:

1. list pages if necessary
2. identify the target page
3. select the correct page
4. confirm URL/title when needed

Never assume page index 0 is the target.

## Navigation

After navigation:

1. wait for the required state
2. inspect a snapshot
3. interact

Do not immediately click after navigation without waiting for the page.

## Interaction

Prefer:

- accessible element
- stable selector
- semantic target

Avoid brittle generated CSS selectors.

## Forms

For forms:

1. identify required fields
2. fill only required fields
3. submit
4. verify result

Do not submit forms repeatedly.

## Downloads/uploads

Treat local file access as sensitive.

Before uploading a local file:

- confirm the file
- confirm the destination
- ensure the upload is explicitly requested

Do not upload arbitrary files discovered in the workspace.

## Destructive actions

For:

- delete
- remove
- publish
- send
- submit
- purchase
- deploy

require explicit user intent if the action has meaningful external consequences.

## Verification

After an interaction, verify the resulting state.

Do not assume success merely because the click operation completed.