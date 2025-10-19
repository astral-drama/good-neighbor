# GOOD--9: Add systemd service with Make install/uninstall commands

**Created:** 2025-10-19T15:48:41.739370+00:00
**Status:** Planning

## Description

Add systemd unit file and Make commands (install-service, uninstall-service) to enable easy deployment and management of the Good Neighbor server as a system service.

Requirements:

- Create systemd unit file for good-neighbor service
- Add 'make install-service' command that:
  - Works from a fresh clone
  - Installs system dependencies if needed
  - Creates/activates Python virtual environment
  - Installs Python dependencies via uv
  - Configures systemd service to run on boot
  - Starts the service immediately
  - Handles permissions correctly
- Add 'make uninstall-service' command that:
  - Stops the service
  - Disables the service from running on boot
  - Removes systemd unit file
  - Optionally cleans up venv (with confirmation)
- Service should:
  - Run as appropriate user (not root)
  - Restart automatically on failure
  - Start after network is available
  - Log to systemd journal
  - Survive system reboots
- Documentation in README or CLAUDE.md for service management

Technical considerations:

- Use systemd user service or system service?
- Handle different Linux distributions if possible
- Proper paths for ExecStart, WorkingDirectory
- Environment variables and configuration
- Port binding considerations (8000 default)

## Acceptance Criteria

- [ ] Define acceptance criteria for this story

## Notes

<!-- Add any additional notes or updates here -->

## Related Issues

<!-- Link to any related issues or stories -->
