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
                    if current_key in (
                        "parents",
                        "keywords",
                        "is-part-of",
                        "is-used-in",
                    ):
                        meta[current_key] = []
                        # Keep current_key active to collect list items, but not multiline
                        in_multiline = False
                        # Don't set current_key = None yet - list items may follow
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
                    # Don't clear current_key - there might be more list items
                elif in_multiline:
                    # Multiline value continuation
                    current_value.append(
                        line[2:].strip() if line.startswith("  ") else line.strip()
                    )
                elif line.startswith("  ") and not line.startswith("  - "):
                    # This is indented content but not a list item and not multiline
                    # This means current_key should be cleared (new key coming)
                    current_key = None
                    in_multiline = False

        # Save last key's value
        if current_key:
            if in_multiline:
                meta[current_key] = "\n".join(current_value).strip()
            else:
                meta[current_key] = current_value[0] if current_value else ""

    return meta, body


def resolve_path_list(
    path_list,
    parent_dir: Path,
    self_dir: Path,
    field_name: str,
    allow_empty: bool = False,
):
    """
    Returns list of resolved paths relative to USE_CASE_DIR (posix, no trailing slash).

    Args:
        path_list: List of path references from frontmatter
        parent_dir: Parent directory of the use case (for resolving ..)
        self_dir: Directory of the use case itself
        field_name: Name of the field being resolved (for error messages)
        allow_empty: If True, empty list is allowed; if False and list is empty, defaults to [".."]
    """
    # Handle case where path_list is string "[]" instead of empty list
    if isinstance(path_list, str):
        if path_list == "[]":
            path_list = []
        else:
            path_list = [path_list]
    paths = path_list or []

    # Default to [".."] if paths is empty and allow_empty is False
    # Root-level is when parent_dir is empty
    is_root_level = not parent_dir or len(parent_dir.parts) == 0
    if not paths and not allow_empty and not is_root_level:
        paths = [".."]
    # If allow_empty is True and paths is empty, keep it empty (don't add default)

    resolved = []
    for path_ref in paths:
        if path_ref == "..":
            if is_root_level:
                # At root level, ".." resolves to empty string (no parent in graph)
                resolved.append("")
            else:
                resolved.append(str(parent_dir.as_posix()))
        elif isinstance(path_ref, str) and path_ref.startswith("/"):
            normalized = path_ref.lstrip("/")
            resolved.append(normalized)
        elif isinstance(path_ref, str):
            # Handle relative paths (e.g., ../client-360/know-your-customer)
            # Resolve relative to self_dir
            base_path = self_dir if self_dir != Path(".") else Path()
            combined = base_path / path_ref
            # Manually resolve .. components
            parts = []
            for part in combined.parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            normalized_path = "/".join(parts) if parts else ""
            resolved.append(normalized_path)
        else:
            raise ValueError(
                f"Invalid {field_name} reference '{path_ref}' in {self_dir}"
            )

    # Sibling-as-parent guard (only for is-part-of)
    if field_name == "is-part-of":
        for p in resolved:
            if Path(p).parent == self_dir.parent and Path(p) != self_dir.parent:
                raise ValueError(
                    f"Sibling cannot be in {field_name}: {p} for {self_dir}"
                )

    return resolved


def resolve_parents(meta_parents, parent_dir: Path, self_dir: Path):
    """
    DEPRECATED: Use resolve_path_list instead.
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
    # Root-level is when parent_dir is empty
    is_root_level = not parent_dir or len(parent_dir.parts) == 0
    if not parents and not is_root_level:
        parents = [".."]

    resolved = []
    for parent in parents:
        if parent == "..":
            if is_root_level:
                # At root level, ".." resolves to empty string (no parent in graph)
                resolved.append("")
            else:
                resolved.append(str(parent_dir.as_posix()))
        elif isinstance(parent, str) and parent.startswith("/"):
            normalized = parent.lstrip("/")
            resolved.append(normalized)
        elif isinstance(parent, str):
            # Handle relative paths (e.g., ../client-360/know-your-customer)
            # Resolve relative to self_dir
            # self_dir is something like "core-record-management" or "client-360/know-your-customer"
            # parent is something like "../client-360/know-your-customer"
            base_path = self_dir if self_dir != Path(".") else Path()
            combined = base_path / parent
            # Manually resolve .. components
            parts = []
            for part in combined.parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            normalized_path = "/".join(parts) if parts else ""
            resolved.append(normalized_path)
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

    # Support both old 'parents' field and new 'is-part-of'/'is-used-in' fields
    is_part_of = meta.get("is-part-of")
    is_used_in = meta.get("is-used-in")
    parents = meta.get("parents")  # For backwards compatibility

    # If old 'parents' field exists and new fields don't, use parents for is-part-of
    if parents is not None and is_part_of is None:
        is_part_of = parents

    is_part_of = is_part_of or []
    is_used_in = is_used_in or []

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

    # Write new fields
    lines.append("is-part-of:")
    if is_part_of:
        for p in is_part_of:
            lines.append(f"  - {p}")
    else:
        lines.append("  []")

    lines.append("is-used-in:")
    if is_used_in:
        for p in is_used_in:
            lines.append(f"  - {p}")
    else:
        lines.append("  []")

    lines.append("---")
    return "\n".join(lines) + "\n\n"
