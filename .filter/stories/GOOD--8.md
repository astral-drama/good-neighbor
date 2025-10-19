# GOOD--8: Integrate widgets API with YAML storage for persistence

**Created:** 2025-10-19T13:13:59.802643+00:00
**Status:** Planning

## Description

## Overview

Migrate the widgets API from in-memory storage to the YAML storage backend so that widgets persist across server restarts.

## Current Behavior

- Widgets API uses in-memory dictionary: `widgets_store: dict[str, Widget] = {}`
- Widgets are lost when the server restarts
- There's a TODO comment indicating this migration was planned

## Desired Behavior

- Widgets should use the YAML storage backend like homepages do
- Widgets should persist to storage.yaml
- Widgets should survive server restarts
- All CRUD operations should automatically persist changes

## Implementation Approach

### 1. Follow Homepage API Pattern

The homepage API already demonstrates the correct pattern (homepages.py:14-24):

```python
from good_neighbor.storage import create_yaml_repositories

repos = create_yaml_repositories()
repos.storage.load()

# Use repos.homepages, repos.users, etc.
```

### 2. Update widgets.py

- Import `create_yaml_repositories` from good_neighbor.storage
- Initialize repositories at module level
- Call `repos.storage.load()` to load existing data
- Replace `widgets_store` dictionary with repository access
- Add `repos.storage.save()` calls after mutations (create, update, delete)

### 3. Update Widget Model

- Verify Widget model has `homepage_id` field (required by YAML storage)
- Update API to accept/use homepage_id in requests
- Default to current user's default homepage if not specified

### 4. Repository Methods Needed

The YAMLStorage already provides:

- `get_widgets()` - Get all widgets
- `set_widget(widget)` - Update/insert widget
- `delete_widget(widget_id)` - Delete widget
- `save()` - Persist to disk

### 5. Update All Endpoints

- **GET /api/widgets/** - Use `repos.storage.get_widgets()`
- **POST /api/widgets/** - Use `repos.storage.set_widget()` + `save()`
- **GET /api/widgets/{id}** - Use `repos.storage.get_widgets()`
- **PUT /api/widgets/{id}** - Use `repos.storage.set_widget()` + `save()`
- **PATCH /api/widgets/{id}/position** - Use `repos.storage.set_widget()` + `save()`
- **DELETE /api/widgets/{id}** - Use `repos.storage.delete_widget()` + `save()`

## Testing

- Create a widget via API
- Verify it appears in storage.yaml
- Restart the server
- Verify the widget still exists
- Update/delete operations should also persist

## Technical Notes

- The YAML storage is already implemented and tested with homepages
- File locking and atomic writes are already handled
- Thread-safe operations are already implemented
- The Widget model serialization is already implemented in yaml_storage.py:311-321

## Acceptance Criteria

- [ ] Define acceptance criteria for this story

## Notes

<!-- Add any additional notes or updates here -->

## Related Issues

<!-- Link to any related issues or stories -->
