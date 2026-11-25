# Antigravity (VS Code / Antigravity IDE)

The plugin installs every skill and subagent under the `cw-` prefix so it
never collides with coding workflows.

## Setup

Copy or symlink `plugin/antigravity/` to one of:

- **Global (all projects):** `~/.gemini/config/plugins/creative-writing-skills/`
- **Workspace (single book):** `<book-repo>/.agents/plugins/creative-writing-skills/`

## First Session

1. Open your book folder in VS Code / Antigravity and ask the agent to run
   `/cw-project-setup` (user-invoked only; agents do not start it on their
   own). It interviews you and creates `AGENTS.md`, the `kb/` layout, and
   initial style files.
2. Start writing by activating `/cw-muse` in chat and describing what you want
   to work on. Antigravity automatically loads your root `AGENTS.md` in every
   session, and `/cw-muse` delegates review, research, and KB capture lanes to
   the `cw-*` subagents (`cw-critic`, `cw-writer`, `cw-kb-lead`,
   `cw-reader-sim`, etc.).
