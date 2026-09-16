# Security

## Reporting a vulnerability

Please do not publish exploit details in a public issue. Open a GitHub issue with minimal non-sensitive reproduction information and mark it clearly as a security report, or contact the repository owner privately through GitHub if sensitive details are required.

## Scope

Windows has the richest provider through built-in PowerShell/CIM. Linux uses /proc plus ss when available; macOS falls back to ps-based discovery. The app never elevates itself.

Pulse collects local operating-system process/network information only. It has no account, backend, telemetry, or remote agent.
