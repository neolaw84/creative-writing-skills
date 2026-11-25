---
name: cw-token-budgeting
description: "Context-aware token budgeting: size estimation, caching, and pruning guidelines. Use to prevent context window overflow when processing large drafts or data corpuses."
model-invocable: true
metadata:
  type: reference
---
# Token Budgeting & Context Management

Manage your token and context budget dynamically. When a project contains large documents, manuscripts, or archives, reading or writing everything in a single prompt will exhaust your context window, degrade performance, or trigger truncation errors.

## Token Budgeting Zones

Before reading files, determine which zone the target files place you in:

*   **Green Zone (<= 128k tokens):** Standard execution. You can load all relevant files.
*   **Yellow Zone (128k - 512k tokens):** Require active context pruning. Reduce character profiles, style files, and prioritize high-level summaries over raw text.
*   **Red Zone (> 512k tokens):** Trigger extreme mitigation patterns. If the corpus size requires map-reduce, execute the following three-step pipeline:
    1.  **Map (Chunking):** Split the source file(s) into segments of no more than 10,000 words. For each segment, write an intermediate summary or fact extraction file to a temporary directory (`work/cache/map_chunk_XX.md`).
    2.  **Reduce (Synthesize):** Once all chunks are mapped, read the temporary files together. Consolidate them into a single, unified profile or style guide.
    3.  **Cleanup:** Delete the temporary chunk files to keep the workspace clean.

---

## Size Detection Heuristics

Run standard Unix commands (`wc`) to estimate the token size of files/directories:

1.  **Words to Tokens:** Run `wc -w <filename>`
    *   *Heuristic:* `Tokens = Word Count * 1.3`
2.  **Lines to Tokens:** Run `wc -l <filename>`
    *   *Heuristic:* `Tokens = Line Count * 10`
3.  **Bytes to Tokens:** Run `wc -c <filename>` or `du -k <filename>`
    *   *Heuristic:* `Tokens = Size in KB * 250` (or `Size in Bytes * 0.25`)

---

## Re-use Policy (Check Before Rebuild)

Before generating any map, outline, summary, style guide, or sample directory:
1.  Check if pre-constructed artifacts (e.g., style guides, chapter maps, plot summaries, or sample excerpts) are already available in the project directories or parent paths.
2.  **Reuse them directly** and do not regenerate or overwrite them unless explicitly requested or if the existing files are corrupted.

---

## Caching & Invalidation Rules

To avoid repeatedly reading massive files:
1.  **Cache Location:** Save intermediate analysis (such as chapter-level summaries, extracted styles, and entity indexes) in the workspace's designated cache directory (e.g., `work/cache/`).
2.  **Naming Convention:** Append the modification timestamp of the source file to the cache filename (e.g., `work/cache/chapter1.md.mtime1718360000.summary.md`).
3.  **Invalidation Rule:** 
    *   Run `stat -c %Y <source_file>` or `ls -l` to check its modification time.
    *   If the source file's modification time is newer than the cache file, invalidate the cache, delete the stale cache file, and generate a new one.

---

## Context Pruning Recipes

When in the **Yellow** or **Red** zones, prune your active context using the following recipes:

*   **Style Reference Files:** Load a maximum of 2 style files that specifically govern the active scene/characters (e.g., narrator's voice, scene type) instead of loading all style guides.
*   **Character Profiles:** Load only the profiles of characters who actively speak or interact in the scene being written/critiqued.
*   **Prior Chapters:** Use high-level plot summaries (`plots/`) for the overarching narrative flow. Only load the full text of the immediately preceding scene or chapter to ensure local flow.
*   **Vocabulary/Glossaries:** Load only domain-specific vocab files (e.g., magic systems, faction-specific terms) relevant to the scene instead of loading the entire project glossary.

---

## Processing Workflows for Large Files

*   **Writing & Revision:** Use targeted line ranges. Do not read or write the entire file; specify targeted line ranges and read only the local context block (+/- 50 lines) surrounding the edits.
*   **Critique & Reader Simulation:** Split the draft into chapter or scene segments of 3k - 5k words. Review each segment individually. At the end of each segment, output a brief "State Payload" (e.g., reader emotional state, unresolved questions, expectations). Load this State Payload alongside the next segment to maintain continuity without loading previous chapters.
*   **Ingestion (Create Agent - Map-Reduce Pattern):** When digesting a large corpus for agent creation, execute this explicit step-by-step pipeline:
    1.  **Analyze & Set Density:** Scan the directory sizes to determine the token zone. Establish the reading target: **at least 50%** of the text for the Yellow Zone, and **at least 25%** for the Red Zone / extremely large corpuses.
    2.  **Map Phase (Chunking & Segment Extraction):**
        - Split the files into logical chunks of max 1MB (~250k tokens), or by chapter/story boundaries.
        - For each chunk, read the first, middle, and last portions.
        - Generate an intermediate chunk summary (aiming for **800 - 1,000 words per 10,000 words** of source text) to preserve local voice, style markers, and specific vocabulary.
        - Save these chunk summaries as separate files in the temporary cache directory (e.g., `work/cache/map_chunk_XX.md`).
    3.  **Reduce Phase (Consolidation & Aggregation):**
        - Load all mapped chunk summaries from the temporary cache directory into the context window.
        - Synthesize the aggregated summaries to build the consolidated lore (`lore/`), character profiles, settings guides, and the style guide (`style/`).
        - Generate the final author agent definition (`agents/<author-slug>.md`) using the consolidated data.
    4.  **Cleanup:** Delete the temporary map chunk files from the cache directory to prevent workspace clutter.
