# GOOD--10: Add query widget type

**Created:** 2025-10-19T17:40:39.468091+00:00
**Status:** Planning

## Description

Implement a new query widget type that allows users to submit text queries to configurable URLs.

## Requirements

### Widget Properties

- **url_template**: Base URL template with placeholder for query (e.g., 'https://claude.ai/new?q={query}' or 'https://google.com/search?q={query}')
- **title**: Widget title/label
- **icon**: Optional emoji icon
- **placeholder**: Optional placeholder text for input field (default: 'Enter query...')

### UI Components

- Text input field for entering queries
- Submit button (or Enter key handler)
- Clean, minimal design consistent with other widget types

### Behavior

- When user presses Enter in text field OR clicks submit button:
  - Replace {query} placeholder in url_template with URL-encoded user input
  - Open resulting URL in new tab/window
- Input field should clear after submission (or optionally retain last query)

### Backend

- Add 'query' to WidgetType enum
- Define QueryWidgetProperties model with required fields
- Update widget creation/update endpoints to handle query widget type

### Frontend

- Create query-widget.ts component extending BaseWidget
- Implement renderNormalView() with input field and submit button
- Implement renderEditView() for configuring widget properties
- Add query widget to widget creation dialog options
- Handle form submission and URL navigation

### Testing

- Add tests for query widget creation, update, delete
- Test URL template replacement with various query strings
- Test special characters and URL encoding
- Test Enter key and button click submission

## Implementation Notes

- URL encoding must handle special characters properly
- Consider adding common URL templates as presets (Google, Claude AI, DuckDuckGo, etc.)
- Query widget should NOT be draggable like shortcuts (stays in place)
- Consider adding keyboard shortcut to focus query input

## Acceptance Criteria

- [ ] Define acceptance criteria for this story

## Notes

<!-- Add any additional notes or updates here -->

## Related Issues

<!-- Link to any related issues or stories -->
