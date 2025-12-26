"""Navigation file generation."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

from .config import USE_CASE_DIR
from .graph import primary_parent


def build_nav(node_id: str, graph: dict, primary: dict) -> List[Any]:
    """
    Build nav list for .pages.yaml for immediate children of node_id
    (no deep nesting; child dirs listed by their directory name, not index.md path).
    """
    base_dir = USE_CASE_DIR / node_id if node_id else USE_CASE_DIR
    dirs = []
    files = []
    for cid, p in primary.items():
        # For root node (node_id == "."), include nodes where primary parent is "." (root-level use cases)
        # AND that are direct children (only one level deep from USE_CASE_DIR)
        # For other nodes, include nodes where p == node_id
        if node_id == ".":
            # Root-level use cases now have parents: [".."] which resolves to ["."]
            # So we check for p == "." instead of p == None
            if p != ".":
                continue
            # Only include direct children: path should be directly under USE_CASE_DIR
            node_path = graph[cid]["path"]
            rel_to_base = node_path.relative_to(USE_CASE_DIR)
            # Count path depth: if it has more than 2 parts, it's nested
            # e.g., "client-360/social-media/index.md" has 3 parts, exclude it
            # e.g., "cyber-security/index.md" has 2 parts, include it
            if len(rel_to_base.parts) > 2:
                continue
        else:
            if p != node_id:
                continue
        rel_path = graph[cid]["path"].relative_to(base_dir).as_posix()
        if graph[cid]["path"].stem == "index":
            # For index.md files, reference the directory, not the file
            # Strip /index.md from the path to get just the directory
            path_obj = Path(rel_path)
            if path_obj.parent == Path("."):
                # This is index.md in the same directory (shouldn't happen for children)
                continue
            # Get the directory name (parent of index.md)
            dir_path = str(path_obj.parent)
            dirs.append(dir_path)
        else:
            # Exclude helper files like strategic-use-cases.md (not real use cases)
            if graph[cid]["path"].name == "strategic-use-cases.md":
                continue
            # Only include .md files that are use case pages
            if graph[cid]["path"].suffix == ".md":
                files.append(rel_path)
    dirs.sort()
    files.sort()
    return dirs + files


def write_pages_yaml(graph: dict):
    """Generate .pages.yaml for every directory that has an index.md use case."""
    primary = primary_parent(graph)

    def write_for(node_id: str):
        node = graph[node_id]
        if node["path"].stem != "index":
            return
        dir_path = node["path"].parent
        nav_entries = build_nav(node_id, graph, primary)
        # Include index.md as the first entry in nav (for consistency with other directories)
        # CRITICAL: index.md MUST be included for mkdocs-awesome-pages-plugin to resolve directory references
        nav_with_index = ["index.md"] + nav_entries
        # Verify index.md is included
        if "index.md" not in nav_with_index:
            raise ValueError(f"BUG: index.md missing from nav_for {node_id}")
        data = {
            "title": node["title"],
            "nav": nav_with_index,
        }
        target = dir_path / ".pages.yaml"
        if yaml:
            content = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
        else:
            # minimal manual formatting
            lines = [f"title: {node['title']}"]
            lines.append("nav:")
            for entry in nav_with_index:
                lines.append(f"  - {entry}")
            content = "\n".join(lines) + "\n"

        # Verify index.md is in the generated content
        if "index.md" not in content:
            raise ValueError(
                f"BUG: index.md missing from generated content for {node_id}"
            )

        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                return
        target.write_text(content, encoding="utf-8")

        # Verify it was written correctly
        written = target.read_text(encoding="utf-8")
        if "index.md" not in written:
            raise ValueError(f"BUG: index.md missing from written file {target}")

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(write_for, graph.keys()))
