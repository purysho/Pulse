<div align="center">
  <img src="assets/icon.svg" width="132" alt="Pulse icon">
  <h1>Pulse</h1>
  <p><strong>A local process and network relationship monitor that shows not just what is running, but what is connected to what.</strong></p>
  <p>
    <a href="https://github.com/purysho/Pulse/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/purysho/Pulse/actions/workflows/ci.yml/badge.svg"></a>
    <a href="https://github.com/purysho/Pulse/releases"><img alt="Releases" src="https://img.shields.io/github/v/release/purysho/Pulse?display_name=tag&sort=semver"></a>
    <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-202832.svg"></a>
    <a href="#download"><img alt="Status: beta" src="https://img.shields.io/badge/status-beta-C9A44C.svg"></a>
  </p>
  <p><strong>Download:</strong> <a href="https://github.com/purysho/Pulse/releases/latest/download/Pulse-Windows-x64.exe">Windows</a> · <a href="https://github.com/purysho/Pulse/releases/latest/download/Pulse-macOS-arm64.zip">macOS</a> · <a href="https://github.com/purysho/Pulse/releases/latest/download/Pulse-Linux-x86_64.tar.gz">Linux</a> · <a href="#run-from-source">Run from source</a> · <a href="https://github.com/purysho/Pulse/issues">Report an issue</a></p>
</div>

![Pulse showing a dev stack's process tree in the Relations view](docs/screenshot.png)

## What it does

- Process list with PID, parent PID, memory, and CPU time
- Filter by process name, PID, path, or command line
- Parent/child relationship view
- Listening and established TCP links where supported
- Configurable automatic refresh
- JSON snapshot export

## Download

| Platform | File |
|---|---|
| Windows 10/11 (x64) | [Pulse-Windows-x64.exe](https://github.com/purysho/Pulse/releases/latest/download/Pulse-Windows-x64.exe) — portable, no installer |
| macOS (Apple Silicon) | [Pulse-macOS-arm64.zip](https://github.com/purysho/Pulse/releases/latest/download/Pulse-macOS-arm64.zip) — unzip and move to Applications |
| Linux (x86_64) | [Pulse-Linux-x86_64.tar.gz](https://github.com/purysho/Pulse/releases/latest/download/Pulse-Linux-x86_64.tar.gz) — extract and run `./Pulse` |

Each [release](https://github.com/purysho/Pulse/releases) is built from the tagged source by GitHub Actions and carries a `SHA256SUMS.txt`. The builds are not yet code-signed, so on first launch Windows SmartScreen may ask you to confirm ("More info" → "Run anyway"), and macOS may need you to Control-click the app and choose **Open**.

**Status: beta.** Pulse does what this README describes and is covered by CI on Windows, macOS and Linux, but it is young: expect rough edges, and please [report them](https://github.com/purysho/Pulse/issues).

## Run from source

Requirements: Python 3.10+ with Tk support.

```powershell
pyw pulse_desktop.pyw
```

The application uses Python's standard library at runtime.

## Build a standalone Windows executable

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows.ps1
```

Output:

```text
dist\Pulse.exe
```

## Privacy

Pulse collects local operating-system process/network information only. It has no account, backend, telemetry, or remote agent.

## Scope

Windows has the richest provider through built-in PowerShell/CIM. Linux uses /proc plus ss when available; macOS falls back to ps-based discovery. The app never elevates itself.

## Release process

- Every push runs tests/compile checks and builds a Windows executable artifact.
- Tags matching `v*` build the executable again, compute SHA256, and publish both files to GitHub Releases.
- See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT
