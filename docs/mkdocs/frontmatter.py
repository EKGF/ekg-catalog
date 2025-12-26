"""Frontmatter parsing and manipulation."""

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def parse_frontmatter(text: str):
    """Parse YAML frontmatter from markdown text."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        return {}, text
    raw_meta = parts[0].strip("-\n")
    body = parts[1].lstrip("-\n")
    if yaml:
        try:
            meta = yaml.safe_load(raw_meta) or {}
        except Exception:
            meta = {}
    else:
        # Minimal fallback parser for simple key/list structures and multiline values
        meta = {}
        current_key = None
        current_value = []
        in_multiline = False

        for line in raw_meta.splitlines():
            stripped = line.strip()
            if not stripped:
                if current_key and in_multiline:
                    current_value.append("")
                continue

            if ":" in line and not line.startswith(" "):
                # Save previous key's value
                if current_key:
                    if in_multiline:
                        meta[current_key] = "\n".join(current_value).strip()
                    else:
                        meta[current_key] = current_value[0] if current_value else ""

                # Parse new key
                parts = line.split(":", 1)
                current_key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ""

                if val == ">-" or val == "|":
                    in_multiline = True
                    current_value = []
                elif val.startswith("- "):
                    # List item on same line
                    if current_key not in meta:
                        meta[current_key] = []
                    meta[current_key].append(val[2:].strip())
                    current_key = None
                    in_multiline = False
                elif val == "" or val == "[]":
                    # Empty value or empty list
                    if current_key == "parents" or current_key == "keywords":
                        meta[current_key] = []
                        current_key = None
                        in_multiline = False
                    else:
                        in_multiline = True
                        current_value = []
                else:
                    meta[current_key] = val
                    current_key = None
                    in_multiline = False
            elif current_key:
                if line.startswith("  - "):
                    # List item
                    if current_key not in meta:
                        meta[current_key] = []
                    meta[current_key].append(line[4:].strip())
                elif in_multiline or line.startswith("  "):
                    # Multiline value continuation
                    current_value.append(
                        line[2:].strip() if line.startswith("  ") else line.strip()
                    )

        # Save last key's value
        if current_key:
            if in_multiline:
                meta[current_key] = "\n".join(current_value).strip()
            else:
                meta[current_key] = current_value[0] if current_value else ""

    return meta, body


def resolve_parents(meta_parents, parent_dir: Path, self_dir: Path):
    """
    Returns list of resolved parent paths relative to USE_CASE_DIR (posix, no trailing slash).
    Defaults to [".."] if parents is empty and this is not a root-level use case.
    """
    # Handle case where parents is string "[]" instead of empty list
    if isinstance(meta_parents, str):
        if meta_parents == "[]":
            meta_parents = []
        else:
            meta_parents = [meta_parents]
    parents = meta_parents or []

    # Default to [".."] if parents is empty and this is not root-level
    if not parents and parent_dir != Path("."):
        parents = [".."]

    resolved = []
    for parent in parents:
        if parent == "..":
            if parent_dir == Path("."):
                resolved.append(".")
            else:
                resolved.append(str(parent_dir.as_posix()))
        elif isinstance(parent, str) and parent.startswith("/"):
            normalized = parent.lstrip("/")
            resolved.append(normalized)
        else:
            raise ValueError(f"Invalid parent reference '{parent}' in {self_dir}")
    # Sibling-as-parent guard
    for p in resolved:
        if Path(p).parent == self_dir.parent and Path(p) != self_dir.parent:
            raise ValueError(f"Sibling cannot be a parent: {p} for {self_dir}")
    return resolved


def format_frontmatter(meta):
    """Format metadata dictionary as YAML frontmatter."""
    title = meta.get("title", "")
    summary = meta.get("summary", "")
    keywords = meta.get("keywords", []) or []
    parents = meta.get("parents", []) or []

    lines = ["---"]
    lines.append("title: >-")
    lines.append(f"  {title}")
    if summary:
        lines.append("summary: >-")
        lines.append(f"  {summary}")
    lines.append("keywords:")
    if keywords:
        for kw in keywords:
            lines.append(f"  - {kw}")
    else:
        lines.append("  []")
    lines.append("parents:")
    if parents:
        for p in parents:
            lines.append(f"  - {p}")
    else:
        lines.append("  []")
    lines.append("---")
    return "\n".join(lines) + "\n\n"
