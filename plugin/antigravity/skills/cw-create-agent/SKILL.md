---
name: cw-create-agent
description: >
  Derive a custom author-mimicking agent and reference library from a corpus of
  an author's previous works: maps, voice-preserving plot summaries, lore,
  verbatim samples, style guides, methodology notes, and an Antigravity agent or
  plugin bundle. User-invoked; run when building a new author persona from
  existing works.
model-invocable: false
metadata:
  type: checkpoint
---
# Create Author Agent

Build a reusable, author-mimicking agent and structured reference library from a
corpus of previous works (and optional brainstorming logs or prompts).

## Skills to Load

Load each skill when its phase needs it:

- `/cw-token-budgeting` — token zones (Green <= 128k, Yellow 128k–512k, Red > 512k),
  size estimation heuristics, `work/cache/` caching and invalidation, context
  pruning, and the map-reduce ingestion pipeline for large corpuses.
- `/cw-craft` (`resources/style-analysis.md`) — style extraction,
  voice dimensions, file splitting, and separating intentional patterns from
  unconscious tics.
- `/cw-story-memory` (`resources/fact-extraction.md`, `resources/kb-layout.md`,
  `resources/story-reference-writing.md`) — extracting canon, character profiles,
  world rules, timelines, and structuring durable reference pages.
- `/cw-story-planning` (`resources/story-architecture.md`) — chapter beat, scene,
  and arc tracking for plot summaries.
- `/cw-writing-principles` — reader reward channels, show-don't-tell discipline,
  and spotting AI prose tells.
- `/cw-shared-dao` — canonical terms, aliases, and domain vocabulary.
- `/cw-llm-writing` — plain, scannable prose for the generated agent prompt and
  reference documentation.

Where subagents are available, you may delegate style extraction to
`cw-style-creator` and lore/canon extraction to `cw-kb-lead` (briefing each with the
relevant samples, maps, and skills).

## Output Structure

Confirm with the author whether they want a standalone **Antigravity plugin
bundle** (recommended for reuse across projects) or a **workspace-local agent**
under `.agents/`.

Default Antigravity plugin layout:

```text
<author-slug>/
├── plugin.json
├── README.md
├── agents/
│   └── <author-slug>.md
└── skills/
    └── <author-slug>/
        ├── SKILL.md
        └── <author-slug>-references/
            ├── brainstorm-notes.md
            ├── lore/
            │   ├── vocab.md
            │   ├── characters/
            │   ├── world/
            │   └── timeline/
            ├── maps/
            ├── plots/
            ├── samples/
            └── style/
```

For a workspace-local agent, place the agent at `.agents/agents/<author-slug>.md`
and the reference library in the project's agreed reference directory (or `kb/`).

## Workflow

1. **Re-use Check**: Before generating maps, plot outlines, summaries, lore,
   style guides, or samples, check whether pre-constructed artifacts already
   exist. Reuse existing artifacts directly; do not regenerate or overwrite them
   without the author's approval.

2. **Scan and Zone the Archive**: Inspect `previous-works/` (or the user's
   specified source folder) and `prompts/` (if any). Use `/cw-token-budgeting`
   size heuristics (`wc -w`, `wc -l`, `wc -c` or equivalent) to classify the
   corpus into the Green, Yellow, or Red zone and follow its reading density
   and map-reduce caching rules (`work/cache/`) when in Yellow or Red.

3. **Map and Summarize Plots (`maps/` and `plots/`)**:
   - Create `maps/` linking each story or chapter to exact line-number ranges
     (`from`–`to`) so later passes can read targeted excerpts without blowing
     context limits.
   - Create chapter-by-chapter summaries in `plots/` following
     `/cw-story-planning` `resources/story-architecture.md`.
   - Aim for **800 – 1,000 words per 10,000 words** of source text so summaries
     preserve local voice, style markers, pacing, and distinctive vocabulary
     rather than dry plot bullets.
   - For large archives, map and summarize one book or chapter at a time and
     write each file before moving on.

4. **Build Lore (`lore/`)**: Extract recurring settings, character profiles,
   chronologies, canonical vocabulary, and "hard rules" of the universe
   (physics, logistics, economics, social rules) using `/cw-story-memory`
   (`resources/fact-extraction.md`, `resources/kb-layout.md`) and `/cw-shared-dao`.
   Organize into `characters/`, `world/`, `timeline/`, and `vocab.md`.

5. **Curate Verbatim Samples (`samples/`) — Hard Quantitative Constraint**:
   - Extract substantial, verbatim, representative passages organized by
     register, genre, or verse — not short illustrative snippets.
   - Hit the corpus zone's verbatim volume target (**20% – 30%** of total raw
     works for Yellow Zone; **10% – 15%** for Red Zone).
   - Add a `samples/README.md` indexing which sample bundle matches which scene
     type or register so writing agents load only one bundle per scene.

6. **Codify Style (`style/`)**: Follow `/cw-craft`
   `resources/style-analysis.md` to produce principle-driven style guides split
   by voice dimension (master style guide, genre/register shifts, dialogue,
   pacing, sensory craft).
   - For Yellow/Red corpuses, derive `style/` primarily from `samples/` and
     `plots/`, consulting the raw archive sparingly via `maps/` line ranges.
   - Separate intentional voice patterns (keep in `style/`) from unconscious
     tics or legacy artifacts (log as things to filter out).

7. **Extract Methodology (`brainstorm-notes.md`)**: Analyze `prompts/` or
   brainstorming logs to document how the author conceives premises, stakes,
   and structure. If no logs exist, infer the author's recurring conceptual
   process from `plots/`, `samples/`, and `style/`, marking inferred points
   explicitly.

8. **Author the Agent and Skill Definitions**:
   - Write `agents/<author-slug>.md` with valid Antigravity subagent
     frontmatter (`name`, `description`, `subagent: true`, `mainAgent: false`,
     `tools: [read_file, edit_file, write_file, run_command, manage_task, search_web]`).
   - Reference the sibling reference library using relative paths
     (`../skills/<author-slug>/<author-slug>-references/...`) with explicit
     context-budgeting rules (e.g., load 1–2 style guides and 1 register-matched
     sample bundle per task).
   - Document the corpus size, token zone, and sampling method used.
   - If building a plugin bundle, also write `skills/<author-slug>/SKILL.md`
     (following `/cw-llm-writing` and `/cw-muse` workflow hooks) and
     `plugin.json`.

9. **Audit Sample Volume (Mandatory)**:
   - Measure total byte/character size of the raw corpus vs. the compiled files
     in `samples/` using a quick script or exact calculation.
   - Compute `(samples_bytes / corpus_bytes) * 100` and report the exact ratio
     in your final summary to the user.
   - If the ratio falls below the zone's target (e.g. < 20% for Yellow Zone or
     < 10% for Red Zone), expand `samples/` and re-verify before finishing.

## Principles

- **Logistics as Engine**: Capture the concrete "how" of the author's world
  (supply chains, economics, physical constraints, social mechanics).
- **Show, Don't Tell**: Ensure style guides and samples highlight how the author
  reveals character and world through action, behavior, and sensory detail
  (`/cw-writing-principles`).
- **Context-Aware Pacing**: Use `maps/` and `plots/` to keep both the derivation
  process and future drafting sessions within context budgets.
- **Hard Volume Auditing**: Treat the `samples/` percentage targets as hard
  requirements; never substitute summary quality for verbatim sample volume.
