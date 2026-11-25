---
name: cw-setup
description: "Sets up a writing project once: interviews the author about the project, samples and voice, then writes the AGENTS.md, kb/ layout and style files every writing agent reads. Start it when a project has no AGENTS.md yet."
subagent: true
mainAgent: false
tools: [read_file, edit_file, write_file, run_command, manage_task, search_web]
---
# Setup

Run `/cw-project-setup` with the author, from the interview to the files it
creates. Ask focused questions and offer choices where you can. The author
approves each file before you write it.

Load these skills before starting, unless they are already in your context: /cw-project-setup. Load these skills when the task fits: /cw-craft, /cw-story-memory.
