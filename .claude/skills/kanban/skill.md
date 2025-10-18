# Kanban Skill

You are a kanban project management specialist using the `filter` CLI tool to manage stories and workflows in git repositories.

## Overview

The `filter` tool is an LLM-powered kanban board system that uses a file-system based approach for managing development stories. It creates a `.filter/` directory in projects to track stories through different workflow stages.

## Filter Directory Structure

```
.filter/
├── config.yml          # Project configuration (prefix, story counter, stages)
├── README.md           # Documentation about the filter project
├── stories/            # Contains all story markdown files
│   ├── PROJ-1.md
│   ├── PROJ-2.md
│   └── ...
└── kanban/            # Kanban board with symlinks to stories
    ├── planning/      # Stories in planning phase
    ├── in-progress/   # Stories currently being worked on
    ├── testing/       # Stories in testing phase
    ├── pr/            # Stories in pull request review
    └── complete/      # Completed stories
```

## Core Concepts

### Stories

- Stories are markdown files stored in `.filter/stories/`
- Each story has a unique ID format: `PREFIX-NUMBER` (e.g., `GOOD-1`, `GOOD-2`)
- The prefix is derived from the project name and configured in `config.yml`
- Story numbers auto-increment from the `last_story_number` in config
- **Stories can be edited** - You can modify story files to update descriptions, add acceptance criteria, or include implementation details

### Kanban Stages

Stories move through these default stages (configurable in `config.yml`):

1. **planning** - Initial planning and requirements gathering
1. **in-progress** - Active development work
1. **testing** - Testing and quality assurance
1. **pr** - Pull request review
1. **complete** - Finished and merged

Stories are represented in kanban stages via symbolic links to the actual markdown file in `stories/`.

## Filter CLI Commands

### Check Tool Status

```bash
filter status
```

Shows if filter tool and dependencies are properly installed.

### Project Management

**Create a new filter project:**

```bash
filter project create
```

This creates the `.filter/` directory structure with config, stories, and kanban directories.

**Get project info:**

```bash
filter project info
```

Shows project configuration, story count, and stage distribution.

**Delete a project:**

```bash
filter project delete
```

Removes the entire `.filter/` directory (use with caution).

### Story Management

**Create a new story:**

```bash
# Create in planning stage (default)
filter story create "Story title"

# Create with description
filter story create "Story title" -d "Detailed description of the story"

# Create in specific stage
filter story create "Story title" -s in-progress
```

**List stories:**

```bash
# List all stories
filter story list

# List all stories with details
filter story list

# List stories in specific stage
filter story list --stage in-progress
filter story list --stage planning
```

**Move a story to different stage:**

```bash
# Move story to next stage in workflow
filter story move GOOD-1 in-progress
filter story move GOOD-1 testing
filter story move GOOD-1 pr
filter story move GOOD-1 complete
```

**Delete a story:**

```bash
filter story delete GOOD-1
```

This removes the story markdown file and all its kanban symlinks.

**Edit a story:**

Stories are markdown files that can be edited directly. Use the Read and Edit tools to modify story content:

```bash
# Read a story to see current content
Read .filter/stories/GOOD-1.md

# Edit to update description, add details, acceptance criteria, etc.
Edit .filter/stories/GOOD-1.md
```

## Story File Format

Stories are markdown files with YAML frontmatter followed by markdown content:

```markdown
---
id: GOOD-1
title: Story title
description: Brief story description
stage: in-progress
created_at: 2025-10-17T12:00:00Z
updated_at: 2025-10-17T14:30:00Z
---

# Story Title

## Description
Detailed description of what needs to be done.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Implementation Notes
Technical details, approach, considerations, etc.

## Testing Notes
How to test this feature, edge cases to consider.

## References
Links to related issues, documentation, designs, etc.
```

### Editable Fields

You can edit any part of a story file:

- **Frontmatter**: Update title, description (but NOT id or stage - use CLI for stage moves)
- **Markdown content**: Add acceptance criteria, implementation notes, testing details, links
- **Structure**: Organize content however is most useful for the story

### When to Edit Stories

Edit story files when you need to:

- Add or refine acceptance criteria
- Document implementation approach or technical decisions
- Add testing notes or edge cases to consider
- Include references to related documentation or issues
- Update description with more details as requirements evolve
- Track progress with checklists
- Add notes discovered during development

## Common Workflows

### Starting New Work

1. Create a story in planning:

   ```bash
   filter story create "Implement user authentication" -d "Add JWT-based auth"
   ```

1. Edit the story to add details:

   ```
   Read .filter/stories/GOOD-1.md
   Edit .filter/stories/GOOD-1.md  # Add acceptance criteria, implementation notes
   ```

1. Move to in-progress when ready to start:

   ```bash
   filter story move GOOD-1 in-progress
   ```

### Refining a Story During Development

1. Read the current story:

   ```
   Read .filter/stories/GOOD-1.md
   ```

1. Edit to add implementation details discovered during work:

   ```
   Edit .filter/stories/GOOD-1.md
   # Add: technical decisions, gotchas, testing notes
   ```

1. Continue development with updated context

### Moving Through Development

1. Work on the feature in your codebase

1. Update story with testing notes:

   ```
   Edit .filter/stories/GOOD-1.md  # Add testing checklist
   ```

1. Move to testing when development is complete:

   ```bash
   filter story move GOOD-1 testing
   ```

1. Run tests and quality checks

1. Create pull request and move to pr stage:

   ```bash
   filter story move GOOD-1 pr
   ```

1. After PR approval and merge, mark complete:

   ```bash
   filter story move GOOD-1 complete
   ```

### Viewing Current Work

```bash
# See what's actively being worked on
filter story list --stage in-progress

# Check what needs review
filter story list --stage pr

# View planning backlog
filter story list --stage planning
```

## Best Practices

### Story Creation

- Use clear, action-oriented titles (e.g., "Add dark mode toggle")
- Include sufficient detail in initial descriptions
- Create stories in `planning` stage by default
- One story per feature or bugfix

### Story Editing

- **Edit freely** - Stories are meant to be living documents
- Add acceptance criteria before starting work
- Document implementation decisions as you make them
- Update with testing notes and edge cases discovered
- Use checklists to track progress within a story
- Keep frontmatter `id` and `stage` unchanged (use CLI to move stages)
- Include links to related PRs, issues, or documentation

### Story Lifecycle

- Only move stories forward through stages (don't skip stages)
- Keep stories in `in-progress` focused (limit work in progress)
- Test thoroughly before moving to `testing` stage
- Move to `complete` only after PR is merged

### Kanban Board Management

- Regularly review `planning` stage to prioritize work
- Keep `in-progress` limited to avoid context switching
- Clear out `complete` periodically (they're archived, not deleted)
- Use `filter story list` frequently to check current state

## Integration with Development

### Before Starting Work

```bash
# Check current project status
filter project info

# List available work
filter story list --stage planning

# Create a story
filter story create "Feature description"

# Edit to add acceptance criteria and details
Read .filter/stories/GOOD-1.md
Edit .filter/stories/GOOD-1.md

# Move to in-progress when ready
filter story move GOOD-1 in-progress
```

### During Development

- Reference story ID in commit messages: `git commit -m "GOOD-1: Add authentication middleware"`
- **Edit story** to add implementation notes, decisions, or discovered requirements
- Update acceptance criteria checklists as you complete them
- Add testing notes for future reference
- Move story through stages as work progresses

### After Completion

```bash
# Update story with final notes if needed
Edit .filter/stories/GOOD-1.md

# Move to complete
filter story move GOOD-1 complete

# Verify completion
filter story list --stage complete
```

## Troubleshooting

### Project Not Initialized

If you see "No filter project found", run:

```bash
filter project create
```

### Viewing Project Configuration

The `.filter/config.yml` file contains project settings:

- `project_name`: Name of the project
- `prefix`: Story ID prefix (e.g., "GOOD-")
- `last_story_number`: Counter for story IDs
- `kanban_stages`: List of workflow stages

### Reading and Editing Stories

Stories are just markdown files in `.filter/stories/`:

- Use `Read .filter/stories/STORY-ID.md` to view
- Use `Edit .filter/stories/STORY-ID.md` to modify
- Use `Glob .filter/stories/*.md` to find all stories

## Key Points to Remember

1. **Always work within a filter-initialized project** - Run `filter project create` if `.filter/` doesn't exist
1. **Use the CLI for stage transitions** - Move stories with `filter story move`
1. **Edit story files directly for content updates** - Add details, criteria, notes freely
1. **Story IDs are immutable** - Once created, a story keeps its ID through all stages
1. **Don't manually edit stage in frontmatter** - Use `filter story move` instead
1. **Stages are directories with symlinks** - The actual story file lives in `stories/`
1. **Stories are living documents** - Update them as you learn and work
1. **Project path matters** - Run filter commands from project root or use `-p` flag

## When to Use This Skill

Invoke this skill when:

- Managing development tasks and stories
- Tracking feature development through workflow stages
- Organizing project backlog and priorities
- Adding or updating story details, acceptance criteria, or notes
- Coordinating work across multiple repositories
- Creating audit trails for development work
- Reading story details to understand requirements

Always use the `filter` CLI tool for kanban operations in filter-managed projects, and feel free to edit story markdown files directly to enhance their content.
