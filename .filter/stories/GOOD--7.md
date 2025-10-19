# GOOD--7: Widget containers: Organize widgets by type in draggable vertical containers

**Created:** 2025-10-19T11:19:53.397460+00:00
**Status:** Planning

## Description

## Overview

Change the layout so that different widget types are organized into separate containers, with containers stacked vertically and reorderable by the user.

## Current Behavior

All widgets currently go into the same container regardless of type.

## Desired Behavior

### Container Organization

- Each widget type should have its own container by default
- Containers should be stacked vertically on the page
- Each container groups widgets of the same type

### Drag and Drop Functionality

- Containers should be reorderable vertically
- A drag handle should appear on the left side of each container on mouse hover
- Users can click and drag the handle to move containers up/down in the vertical list

### Flexibility

- While the default behavior organizes widgets by type into separate containers
- The design should allow users to move individual widgets between any containers
- This provides flexibility for custom organization beyond type-based grouping

## Technical Considerations

- Need to track container order in state/storage
- Implement drag-and-drop UI for container reordering
- Maintain widget-to-container relationships
- Consider container styling and hover states for drag handles

## Acceptance Criteria

- [ ] Define acceptance criteria for this story

## Notes

<!-- Add any additional notes or updates here -->

## Related Issues

<!-- Link to any related issues or stories -->
