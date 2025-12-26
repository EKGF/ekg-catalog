"""Use case graph building."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict

from .config import USE_CASE_DIR
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

    parents = meta.get("parents")
    # Default to [".."] if parents is None or empty list
    # All use cases should have parents: - .. (root-level ones reference use-case/index.md)
    # Handle both None and empty list cases
    if parents is None or (isinstance(parents, list) and len(parents) == 0):
        parents = [".."]
    resolved_parents = resolve_parents(parents, parent_dir, self_dir)

    new_meta = {
        "title": title,
        "summary": summary,
        "keywords": keywords,
        "parents": parents,  # keep original expression (e.g., '..' or absolute)
    }
    new_front = format_frontmatter(new_meta)
    new_text = new_front + body
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return {
        "title": title,
        "summary": summary,
        "keywords": keywords,
        "parents": resolved_parents,
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
            node_id = str(rel.parent.as_posix())
            parent_dir = rel.parent.parent if rel.parent != Path(".") else Path(".")
            self_dir = rel.parent
        else:
            node_id = str(rel.with_suffix("").as_posix())
            parent_dir = rel.parent
            self_dir = Path(node_id)
        return node_id, md_path, parent_dir, self_dir

    work_items = [prepare(p) for p in md_files]

    def worker(item):
        node_id, md_path, parent_dir, self_dir = item
        try:
            data = update_frontmatter(md_path, parent_dir, self_dir)
            return (
                node_id,
                {
                    "path": md_path,
                    "title": data["title"],
                    "parents": data["parents"],
                    "children": set(),
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

    # validate parents existence and sibling rule (serial)
    for node_id, info in nodes.items():
        for parent in info["parents"]:
            if parent not in nodes:
                raise ValueError(f"Parent '{parent}' not found for {node_id}")
            # Prevent self-loops: don't add node to its own children
            if parent == node_id:
                continue
            if (
                Path(parent).parent == Path(node_id).parent
                and Path(parent) != Path(node_id).parent
            ):
                raise ValueError(f"Siblings cannot be parents: {parent} for {node_id}")
            nodes[parent]["children"].add(node_id)
    return nodes


def primary_parent(graph: dict) -> Dict[str, str]:
    """Return mapping of node_id -> primary parent (first) or None."""
    mapping = {}
    for node_id, info in graph.items():
        mapping[node_id] = info["parents"][0] if info["parents"] else None
    return mapping
