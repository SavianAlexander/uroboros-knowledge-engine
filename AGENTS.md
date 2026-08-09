

# Tududi Task Master Orchestration (CRITICAL DIRECTIVE)

**CRITICAL DIRECTIVE**: You are required to use the Task Master (Tududi) for ALL project orchestration, task management, and auditing. This applies to all models, subagents, and projects you work on within this environment.

When you are asked to begin a new project, execute a task, or do multi-step work:
1. **Never use local markdown files (`task.md` or similar) for your checklists or planning.** 
2. **You MUST use the `tududi` MCP tools** (`create_project`, `create_task`, `add_subtask`, `update_task`, `complete_task`) to log your tasks, track your progress, and manage checklists.
3. Ensure you map all items properly (e.g. tag with `Antigravity`, set proper `due_date`, and assign under the correct project). 
4. All activity logged through the `tududi` MCP tools will automatically sync to the user's account (`savianalexander@pm.me`).

By adhering to this rule, Task Master serves as the absolute single source of truth for all agentic operations and project states.

## Comprehensive Tududi MCP Tool Reference & Commands

All models and subagents must invoke these tools via `call_mcp_tool` (ServerName: `tududi`) across all workspace projects:

### 1. Projects Management
- `list_projects`: List all active projects.
- `get_project`: Retrieve project details by ID.
- `create_project`: Create a new project (`name` required, `description`, `status`, `priority`, `area_id`).
- `update_project`: Update project properties (`uid` required, `name`, `description`, `status`, `priority`).
- `delete_project`: Remove a project by ID.

### 2. Task Management & Orchestration
- `list_tasks`: Query tasks (`project_id`, `status`).
- `get_task`: Retrieve task details and nested subtasks.
- `create_task`: Create a top-level task (`name` required, `project_id`, `note`, `priority`, `due_date`, `tags: ["Antigravity"]`).
- `add_subtask`: Add a nested sub-task (`parent_task_id`, `name`).
- `update_task`: Update task properties (`id`, `name`, `status`, `priority`, `note`).
- `complete_task`: Mark task/subtask complete (`id`, `status: 2`) with completion timestamp.
- `delete_task`: Delete a task by ID.
- `get_task_metrics`: Query productivity stats and completion metrics.

### 3. Inbox, Habits, Notes, & Goals
- **Inbox**: `list_inbox`, `add_to_inbox`, `get_inbox_item`, `update_inbox_item`, `process_inbox_item`, `delete_inbox_item`
- **Habits**: `list_habits`, `get_habit`, `create_habit`, `update_habit`, `delete_habit`, `log_habit_completion`, `get_habit_completions`, `delete_habit_completion`, `get_habit_stats`
- **Notes**: `list_notes`, `get_note`, `create_note`, `update_note`, `delete_note`
- **Areas & Tags**: `list_areas`, `get_area`, `create_area`, `update_area`, `delete_area`, `list_tags`, `get_tag`, `create_tag`, `update_tag`, `delete_tag`
- **Goals & People**: `list_goals`, `get_goal`, `create_goal`, `update_goal`, `delete_goal`, `list_people`, `get_person`, `create_person`, `update_person`, `delete_person`
- **Search & Views**: `search`, `list_views`, `get_view`, `create_view`, `update_view`, `delete_view`
