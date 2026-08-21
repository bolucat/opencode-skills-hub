# Chrome Debug Skill

Token-efficient Chrome debugging skill for OpenCode + Chrome DevTools MCP.

## Structure

```text
chrome-debug/
├── SKILL.md
└── references/
    ├── debugging-workflow.md
    ├── console-debugging.md
    ├── network-debugging.md
    ├── dom-and-ui.md
    ├── javascript-runtime.md
    ├── performance.md
    ├── browser-automation.md
    ├── token-efficiency.md
    └── security.md
```

## Design

`SKILL.md` contains decision rules and the default workflow.

`references/` contains detailed procedures that should only be loaded when relevant.

This is intentionally designed for progressive disclosure and low context usage.

## MCP

Designed for Chrome DevTools MCP.

Useful categories include:

- debugging
- network
- performance
- automation
- emulation

Do not enable unnecessary MCP categories when they are not required.

## Recommended browser

Use a dedicated development Chrome profile.

Avoid connecting an everyday personal browser profile containing sensitive authenticated sessions.