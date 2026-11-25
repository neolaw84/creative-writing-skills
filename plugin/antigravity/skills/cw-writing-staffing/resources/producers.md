# Producers

Agents that write or gather: prose, options, outlines, style files, research,
simulated conversation, and kb updates.

## `cw-writer`

Spawn it for the prose passes `/cw-story-workflow` § Produce hands off. Name the mode from `/cw-craft`
`resources/prose-modes.md` (fresh draft, revision, bridge, alternate take, line
polish) and the path to write to. Tell it to load `/cw-character-sim` for voice
fidelity and `/cw-shared-dao` when the scene uses project vocabulary.

One writer per scene: voice consistency degrades when several writers handle
adjacent content.

## `cw-brainstormer`

Run parallel lanes on different angles, not the same angle: three perspectives
beat five instances of one. Tell it to load `/cw-character-sim` for character
arcs, and spawn `cw-creative-researcher` alongside it for real-world grounding.

## `cw-outliner`

Outlining starts after the author confirms direction; brainstorm first.

## `cw-character-sim`

Name the scenario or relationship to explore. Run one lane per character or
perspective for independent exploration, or one shared simulation to test how
they interact.

## `cw-kb-lead`

Tell it to load `/cw-story-memory` for the fiction-specific fact categories and
kb layout. When to spawn it and what its brief carries are in
`/cw-story-workflow` § After Work Settles.
