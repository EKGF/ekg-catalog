"""Use case graph building."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict

from .constants import USE_CASE_DIR
from .frontmatter import parse_frontmatter, resolve_parents, format_frontmatter
from .content import (
    extract_title_and_description,
    extract_summary_section,
    extract_proper_summary,
    extract_keywords,
    remove_diagram_tags,
    remove_h1_from_markdown,
)


def update_frontmatter(path: Path, parent_dir: Path, self_dir: Path):
    """Update frontmatter for a use case file."""
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    # Migrate old 'description' field to 'summary' if it exists
    if "description" in meta and "summary" not in meta:
        meta["summary"] = meta.pop("description")
    # Remove diagram tags (they're injected by template)
    body = remove_diagram_tags(body)

    # Extract summary section and remove it from body if it exists
    summary_text, body_without_summary = extract_summary_section(body)
    if summary_text:
        body = body_without_summary

    # Remove H1 headings from markdown body for use case pages (template will show it)
    # This prevents duplicate H1s in the rendered HTML
    body = remove_h1_from_markdown(body)

    title_body, _ = extract_title_and_description(body)

    title = meta.get("title") or title_body or path.stem.replace("-", " ").title()

    # Summary: frontmatter is leading, but extract if missing or incomplete
    summary = meta.get("summary")
    if not summary or len(summary) < 50 or summary.endswith(":"):
        # Extract proper summary from content
        summary = extract_proper_summary(body)
        if not summary:
            raise ValueError(f"Missing 'summary' field in frontmatter for {path}")

    keywords = meta.get("keywords")
    if not keywords:
        keywords = extract_keywords(title, summary)

    # Support both old 'parents' field and new 'is-part-of'/'is-used-in' fields
    from .frontmatter import resolve_path_list

    # Get field values
    is_part_of = meta.get("is-part-of")
    is_used_in = meta.get("is-used-in")
    parents = meta.get("parents")  # For backwards compatibility

    # Migration logic: if old 'parents' field exists and new fields don't
    if parents is not None and is_part_of is None and is_used_in is None:
        # Old format: first parent is is-part-of, rest are is-used-in
        if isinstance(parents, list) and len(parents) > 0:
            is_part_of = [parents[0]]
            is_used_in = parents[1:] if len(parents) > 1 else []
        else:
            is_part_of = parents
            is_used_in = []

    # Default to [".."] only if is-part-of is None (not if it's explicitly [])
    # Explicit [] means "standalone use case with no ownership parent"
    # Use 'is None' check, not falsy check, to distinguish None from []
    if is_part_of is None:
        is_part_of = [".."]
    if is_used_in is None:
        is_used_in = []

    # Ensure they are lists
    if not isinstance(is_part_of, list):
        is_part_of = [is_part_of] if is_part_of else []
    if not isinstance(is_used_in, list):
        is_used_in = [is_used_in] if is_used_in else []

    # For standalone use cases at root level with no ownership parent,
    # keep is-part-of as [] instead of [".."]
    is_root_level = not parent_dir or len(parent_dir.parts) == 0
    if is_root_level and is_part_of == [".."] and len(is_used_in) > 0:
        # This is a standalone reusable use case - no ownership parent
        is_part_of = []

    # Resolve paths (allow_empty=True to support standalone use cases with is-part-of: [])
    resolved_is_part_of = resolve_path_list(
        is_part_of, parent_dir, self_dir, "is-part-of", allow_empty=True
    )
    resolved_is_used_in = resolve_path_list(
        is_used_in, parent_dir, self_dir, "is-used-in", allow_empty=True
    )

    new_meta = {
        "title": title,
        "summary": summary,
        "keywords": keywords,
        "is-part-of": is_part_of,  # keep original expression (e.g., '..' or absolute or [])
        "is-used-in": is_used_in,  # keep original expression
    }
    new_front = format_frontmatter(new_meta)
    new_text = new_front + body
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return {
        "title": title,
        "summary": summary,
        "keywords": keywords,
        "is-part-of": resolved_is_part_of,
        "is-used-in": resolved_is_used_in,
        # Keep 'parents' for backwards compatibility (combines both fields)
        "parents": resolved_is_part_of + resolved_is_used_in,
        "body": body,
    }


def build_graph(max_workers: int = 8):
    """Build the use case graph from all markdown files."""
    md_files = [p for p in USE_CASE_DIR.rglob("*.md") if not p.name.startswith("_")]
    nodes = {}
    errors = []

    def prepare(md_path: Path):
        rel = md_path.relative_to(USE_CASE_DIR)
        if md_path.stem == "index":
            # Skip root node (use-case/index.md) - Rule 6: there is no single root node
            # Root node is when rel.parent is empty (the USE_CASE_DIR itself)
            if rel.parent == Path() or len(rel.parent.parts) == 0:
                return None
            node_id = str(rel.parent.as_posix())
            # For top-level use cases, parent_dir is empty (USE_CASE_DIR itself)
            # For nested use cases, parent_dir is the parent directory
            parent_dir = rel.parent.parent if len(rel.parent.parts) > 0 else Path()
            self_dir = rel.parent
        else:
            node_id = str(rel.with_suffix("").as_posix())
            parent_dir = rel.parent
            self_dir = Path(node_id)
        return node_id, md_path, parent_dir, self_dir

    work_items = [item for p in md_files if (item := prepare(p)) is not None]
    # Sort work items for deterministic processing order
    work_items.sort(key=lambda x: x[0])

    def worker(item):
        node_id, md_path, parent_dir, self_dir = item
        try:
            data = update_frontmatter(md_path, parent_dir, self_dir)
            return (
                node_id,
                {
                    "path": md_path,
                    "title": data["title"],
                    "is-part-of": data["is-part-of"],
                    "is-used-in": data["is-used-in"],
                    "parents": data["parents"],  # Combined for backwards compat
                    "children": set(),
                    "part-of-children": set(),  # Children via is-part-of
                    "used-in-children": set(),  # Children via is-used-in
                },
                None,
            )
        except Exception as exc:
            return node_id, None, exc

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(worker, item): item[0] for item in work_items}
        for fut in as_completed(futures):
            node_id = futures[fut]
            node_id, result, err = fut.result()
            if err:
                errors.append((node_id, err))
            else:
                nodes[node_id] = result

    if errors:
        msgs = "\n".join(f"{n}: {e}" for n, e in errors)
        raise ValueError(f"Errors while building graph:\n{msgs}")

    # validate is-part-of and is-used-in existence and populate children sets (serial)
    # Sort by node_id for deterministic child set population order
    for node_id, info in sorted(nodes.items()):
        # Process is-part-of relationships
        for parent in info["is-part-of"]:
            # Skip empty parent - it's valid for top-level use cases but excluded from graph per Rule 6
            if not parent or parent == "":
                continue
            if parent not in nodes:
                raise ValueError(f"is-part-of '{parent}' not found for {node_id}")
            # Prevent self-loops: don't add node to its own children
            if parent == node_id:
                continue
            if (
                Path(parent).parent == Path(node_id).parent
                and Path(parent) != Path(node_id).parent
            ):
                raise ValueError(
                    f"Siblings cannot be in is-part-of: {parent} for {node_id}"
                )
            nodes[parent]["children"].add(node_id)
            nodes[parent]["part-of-children"].add(node_id)

        # Process is-used-in relationships
        for parent in info["is-used-in"]:
            # Skip empty parent
            if not parent or parent == "":
                continue
            if parent not in nodes:
                raise ValueError(f"is-used-in '{parent}' not found for {node_id}")
            # Prevent self-loops
            if parent == node_id:
                continue
            # is-used-in can reference siblings (it's a usage relationship, not ownership)
            nodes[parent]["children"].add(node_id)
            nodes[parent]["used-in-children"].add(node_id)

    return nodes


def primary_parent(graph: dict) -> Dict[str, str]:
    """Return mapping of node_id -> primary parent (is-part-of[0]) or None."""
    mapping = {}
    # Use sorted keys for deterministic iteration order
    for node_id in sorted(graph.keys()):
        info = graph[node_id]
        # Primary parent is the is-part-of parent (there should only be 0 or 1)
        mapping[node_id] = info["is-part-of"][0] if info["is-part-of"] else None
    return mapping
