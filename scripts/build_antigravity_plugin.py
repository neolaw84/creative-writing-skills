#!/usr/bin/env python3
"""Build the Antigravity plugin tree at `plugin/antigravity/` from `plugin/claude/`.

Why `plugin/claude/` as the source:
`meridian mars build plugin` has already resolved and bundled external
dependencies (`meridian-base` and `writing-sync`) into `plugin/claude/`.
This script converts that self-contained tree into an Antigravity-native
plugin without modifying upstream `agents/`, `skills/`, or `plugin/claude/`.

Naming convention:
- `creative-writing-muse` -> `cw-muse`
- `creative-writing-craft` -> `cw-craft`
- All other skills `<name>` -> `cw-<name>`
- All agents `<name>` -> `cw-<name>`

Usage:
    python scripts/build_antigravity_plugin.py
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "plugin" / "claude"
EXTRA_SKILLS_SRC = REPO / "skills"
DEST = REPO / "plugin" / "antigravity"

SKILL_ALIASES = {
    "creative-writing-muse": "cw-muse",
    "creative-writing-craft": "cw-craft",
}

READ_ONLY_AGENTS = {
    "critic",
    "reader-sim",
    "continuity-checker",
    "cold-reader",
    "explorer",
    "session-miner",
}
RESEARCH_AGENTS = {"creative-researcher"}
FULL_TOOLS = [
    "read_file",
    "edit_file",
    "write_file",
    "run_command",
    "manage_task",
    "search_web",
]

ANTIGRAVITY_WALKTHROUGH = """# Antigravity (VS Code / Antigravity IDE)

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
"""


def map_skill(name: str) -> str:
    return SKILL_ALIASES.get(name, f"cw-{name}")


def map_agent(name: str) -> str:
    return f"cw-{name}"


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_yaml, body) from a markdown file."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1 :])
    return "", text


def parse_simple_yaml(fm: str) -> dict[str, object]:
    """Parse the simple YAML frontmatter subset used in Claude agents/skills."""
    data: dict[str, object] = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            i += 1
            continue
        key, val = match.group(1), match.group(2).strip()
        if val in {"|", ">", "|-", ">-"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            data[key] = "\n".join(block).strip()
            continue
        if val == "":
            items: list[str] = []
            i += 1
            while i < len(lines) and re.match(r"^\s*-\s+", lines[i]):
                items.append(re.sub(r"^\s*-\s+", "", lines[i]).strip())
                i += 1
            data[key] = items
            continue
        if (val.startswith("'") and val.endswith("'")) or (
            val.startswith('"') and val.endswith('"')
        ):
            val = val[1:-1].replace("''", "'")
        data[key] = val
        i += 1
    return data


def yaml_quote(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def rewrite_references(
    text: str,
    skills: set[str],
    agents: set[str],
    package_name: str,
) -> str:
    """Rewrite Claude-namespaced skill refs and backticked agent refs to cw-*."""

    def replace_namespaced(match: re.Match[str]) -> str:
        slash = match.group(1) or ""
        target = match.group(2)
        if target in skills:
            return f"{slash}{map_skill(target)}"
        if target in agents:
            return map_agent(target)
        return match.group(0)

    text = re.sub(
        rf"(/){re.escape(package_name)}:([a-z0-9][a-z0-9-]*)|(?<![A-Za-z0-9_-]){re.escape(package_name)}:([a-z0-9][a-z0-9-]*)(?![A-Za-z0-9_-])",
        lambda m: (
            f"/{map_skill(m.group(2))}"
            if m.group(2) and m.group(2) in skills
            else (
                map_agent(m.group(2))
                if m.group(2) and m.group(2) in agents
                else (
                    map_skill(m.group(3))
                    if m.group(3) and m.group(3) in skills
                    else (
                        map_agent(m.group(3))
                        if m.group(3) and m.group(3) in agents
                        else m.group(0)
                    )
                )
            )
        ),
        text,
    )

    # Rewrite backticked bare skill references (`/skill`)
    def replace_bare_skill(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in skills:
            return f"`/{map_skill(name)}`"
        return match.group(0)

    text = re.sub(r"`/([a-z][a-z0-9-]*)`", replace_bare_skill, text)

    # Rewrite backticked agent names (`writer`, `critic`, `kb-lead`, etc.)
    def replace_backticked_agent(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in agents:
            return f"`{map_agent(name)}`"
        return match.group(0)

    text = re.sub(r"`([a-z][a-z0-9-]*)`", replace_backticked_agent, text)
    return text


def agent_tools(name: str, disallowed: list[str]) -> list[str]:
    if name in READ_ONLY_AGENTS or ("Edit" in disallowed and "Write" in disallowed):
        return ["read_file"]
    if name in RESEARCH_AGENTS:
        return ["read_file", "search_web"]
    return list(FULL_TOOLS)


def convert_agent(
    src_path: Path,
    dest_path: Path,
    skills: set[str],
    agents: set[str],
    package_name: str,
) -> None:
    raw = src_path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(raw)
    meta = parse_simple_yaml(fm_text)

    orig_name = str(meta.get("name") or src_path.stem)
    new_name = map_agent(orig_name)
    desc = str(meta.get("description") or "").strip()
    disallowed = [str(x) for x in meta.get("disallowedTools", [])]  # type: ignore[union-attr]
    tools = agent_tools(orig_name, disallowed)

    new_fm = "\n".join(
        [
            "---",
            f"name: {new_name}",
            f"description: {yaml_quote(desc)}",
            "subagent: true",
            "mainAgent: false",
            f"tools: [{', '.join(tools)}]",
            "---",
        ]
    )
    new_body = rewrite_references(body, skills, agents, package_name)
    dest_path.write_text(new_fm + new_body, encoding="utf-8")


def convert_skill_md(
    src_path: Path,
    dest_path: Path,
    orig_skill: str,
    skills: set[str],
    agents: set[str],
    package_name: str,
) -> None:
    raw = src_path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(raw)
    new_skill = map_skill(orig_skill)

    # Update `name:` in frontmatter while preserving other fields cleanly
    fm_lines = fm_text.splitlines()
    updated_fm_lines: list[str] = []
    replaced_name = False
    for line in fm_lines:
        if re.match(r"^name:\s*", line):
            updated_fm_lines.append(f"name: {new_skill}")
            replaced_name = True
        else:
            updated_fm_lines.append(line)
    if not replaced_name:
        updated_fm_lines.insert(0, f"name: {new_skill}")

    new_body = rewrite_references(body, skills, agents, package_name)

    if orig_skill == "project-setup":
        new_body = new_body.replace(
            "- `resources/meridian-cli.md`",
            "- `resources/antigravity.md` — Google Antigravity (VS Code / Antigravity IDE) with this plugin.\n- `resources/meridian-cli.md`",
        )

    dest_path.write_text(
        "---\n" + "\n".join(updated_fm_lines) + "\n---" + new_body,
        encoding="utf-8",
    )


def build_plugin_json(src_meta: dict[str, object]) -> dict[str, object]:
    author_raw = src_meta.get("author")
    if isinstance(author_raw, dict):
        author = str(author_raw.get("name", ""))
    else:
        author = str(author_raw or "")

    return {
        "name": str(src_meta.get("name", "creative-writing-skills")),
        "displayName": "Creative Writing Skills",
        "version": str(src_meta.get("version", "0.1.0")),
        "description": (
            "Composable subagents and skills for creative writing projects. "
            "Run /cw-project-setup once per book, then activate /cw-muse as "
            "your creative partner to brainstorm, draft, critique, and maintain "
            "your story's knowledge base."
        ),
        "author": author,
        "homepage": str(src_meta.get("homepage", "")),
        "repository": str(src_meta.get("homepage", "")),
        "suggestedPrompts": [
            "Run /cw-project-setup to initialize a new book project in this workspace",
            "Activate /cw-muse to brainstorm and outline my story premise",
            "Activate /cw-muse to draft or critique the next chapter using my kb/ style and canon",
        ],
    }


def main() -> int:
    src_plugin_json = json.loads(
        (SRC / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    package_name = str(src_plugin_json["name"])

    skill_sources: dict[str, Path] = {
        p.parent.name: p.parent for p in (SRC / "skills").glob("*/SKILL.md")
    }
    if EXTRA_SKILLS_SRC.is_dir():
        for p in EXTRA_SKILLS_SRC.glob("*/SKILL.md"):
            skill_sources.setdefault(p.parent.name, p.parent)

    skills = set(skill_sources)
    agents = {p.stem for p in (SRC / "agents").glob("*.md")}

    if DEST.exists():
        shutil.rmtree(DEST)
    (DEST / "agents").mkdir(parents=True)
    (DEST / "skills").mkdir(parents=True)

    # 1. plugin.json
    (DEST / "plugin.json").write_text(
        json.dumps(build_plugin_json(src_plugin_json), indent=2) + "\n",
        encoding="utf-8",
    )

    # 2. Agents
    for agent_path in sorted((SRC / "agents").glob("*.md")):
        out_name = f"{map_agent(agent_path.stem)}.md"
        convert_agent(agent_path, DEST / "agents" / out_name, skills, agents, package_name)

    # 3. Skills (plugin/claude/skills + any fork-added skills in skills/)
    for orig_skill, skill_dir in sorted(skill_sources.items()):
        new_skill = map_skill(orig_skill)
        out_skill_dir = DEST / "skills" / new_skill
        shutil.copytree(skill_dir, out_skill_dir)

        for md_file in out_skill_dir.rglob("*.md"):
            if md_file.name == "SKILL.md" and md_file.parent == out_skill_dir:
                convert_skill_md(
                    skill_dir / "SKILL.md",
                    md_file,
                    orig_skill,
                    skills,
                    agents,
                    package_name,
                )
            else:
                content = md_file.read_text(encoding="utf-8")
                md_file.write_text(
                    rewrite_references(content, skills, agents, package_name),
                    encoding="utf-8",
                )

        if orig_skill == "project-setup":
            (out_skill_dir / "resources" / "antigravity.md").write_text(
                ANTIGRAVITY_WALKTHROUGH, encoding="utf-8"
            )

    print(
        f"Built {DEST.relative_to(REPO)} with {len(agents)} agents and {len(skills)} skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
