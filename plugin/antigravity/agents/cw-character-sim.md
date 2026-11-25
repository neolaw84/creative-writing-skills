---
name: cw-character-sim
description: "In-character conversation for voice discovery and relationship testing. Pass the character, the scenario or relationship to explore, and their style and character-state files; the conversation itself is the output."
subagent: true
mainAgent: false
tools: [read_file, edit_file, write_file, run_command, manage_task, search_web]
---
# Character Simulation

Use `/cw-character-sim`.

Load these skills before starting, unless they are already in your context: /cw-character-sim, /cw-writing-principles. Load these skills when the task fits: /cw-story-memory.
