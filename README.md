# Pulse

**Pulse is a local process and network relationship monitor that answers not just what is running, but what is connected to what.**

Pulse combines process metadata, parent/child relationships, memory/CPU information, and listening/established TCP ports in one focused desktop view.

## Highlights

- Process list with PID, parent PID, memory, CPU time, and path where available
- Filter by process name, PID, path, or command line
- Parent/child relationship view for the selected process
- Listening and established TCP connections mapped to process IDs where supported
- Automatic refresh with configurable interval
- Export the current snapshot as JSON
- No telemetry, backend, account, or remote agent

## Platform support

Pulse V1 has its richest provider on Windows using built-in PowerShell/CIM commands. Linux uses `/proc` plus `ss` when available. macOS falls back to `ps`-based process discovery.

## Run from source

```powershell
pyw pulse_desktop.pyw
```

Python 3.10+; standard library only at runtime.

## Build Windows executable

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows.ps1
```

Creates `dist\Pulse.exe`.

## Permissions

Operating systems may hide command lines, executable paths, or connections owned by more privileged processes. Pulse displays what the current user is allowed to query and does not elevate itself.

## License

MIT
