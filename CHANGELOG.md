# Changelog

All notable changes to Pulse are documented here.

## [1.1.0] - 2026-09-26

### Added
- Release builds for macOS (Apple Silicon) and Linux (x86_64) alongside Windows, with one `SHA256SUMS.txt` per release.
- A `--pid` argument that opens Pulse focused on one process, used by Switchyard's tool handoff.
- The application icon, which the Windows executable was missing.
- A screenshot of the running app in the README.

### Changed
- CI builds the macOS and Linux packages on every push.

## [1.0.0] - 2026-09-16

### Added
- Polished public release documentation and screenshot.
- Cross-platform CI checks plus Windows executable build artifact.
- Automated tagged GitHub Release workflow with SHA256 checksum.
- Issue templates and security/reporting guidance.

### Current product
- Process list with PID, parent PID, memory, and CPU time
- Filter by process name, PID, path, or command line
- Parent/child relationship view
- Listening and established TCP links where supported
- Configurable automatic refresh
- JSON snapshot export
