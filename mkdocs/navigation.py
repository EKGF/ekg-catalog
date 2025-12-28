"""Navigation file generation."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

from .constants import USE_CASE_DIR
from .graph import primary_parent


def build_nav(node_id: str, graph: dict, primary: dict) -> List[Any]:
    """
    Build nav list for .pages.yaml for immediate children of node_id
    (no deep nesting; child dirs listed by their directory name, not index.md path).
    """
    base_dir = USE_CASE_DIR / node_id if node_id else USE_CASE_DIR
    dirs = []
    files = []

    # Check if this is root-level navigation (use-case/.pages.yaml)
    # Root-level nodes have only one path part (e.g., "client-360")
    is_root_level = len(Path(node_id).parts) == 1 if node_id else True

    # Use sorted items for deterministic navigation order
    for cid in sorted(primary.keys()):
        p = primary[cid]
        # Skip if child not in graph (shouldn't happen, but safety check)
        if cid not in graph:
            continue

        # For root-level navigation (when node_id is empty), find top-level use cases
        # Top-level use cases are directly under USE_CASE_DIR (exactly 2 path parts)
        if not node_id:
            node_path = graph[cid]["path"]
            rel_to_base = node_path.relative_to(USE_CASE_DIR)
            # Top-level: exactly 2 parts (e.g., "client-360/index.md")
            if len(rel_to_base.parts) != 2:
                continue
            # Top-level use cases have no valid parent in the graph (their parent would have been root)
            # Check if this is a top-level use case by path depth (one part: "client-360")
            if len(Path(cid).parts) != 1:
                continue
            # Top-level use cases have empty parent (resolved from ".." at root level)
            if p and p != "":
                continue
        else:
            if p != node_id:
                continue
        rel_path = graph[cid]["path"].relative_to(base_dir).as_posix()
        if graph[cid]["path"].stem == "index":
            # For index.md files, reference the directory, not the file
            # Strip /index.md from the path to get just the directory
            path_obj = Path(rel_path)
            if path_obj.parent == Path() or len(path_obj.parent.parts) == 0:
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
    result = dirs + files
    
    # For root-level navigation, move "other" to the end
    if not node_id and "other" in result:
        result.remove("other")
        result.append("other")
    
    return result


def write_pages_yaml(graph: dict):
    """Generate .pages.yaml for every directory that has an index.md use case."""
    primary = primary_parent(graph)

    # Generate navigation for root-level (use-case/.pages.yaml)
    # Find all top-level use cases (those directly under USE_CASE_DIR)
    root_nav_entries = build_nav("", graph, primary)
    if root_nav_entries:
        root_data = {
            "title": "Use Cases",
            "nav": root_nav_entries,
        }
        root_target = USE_CASE_DIR / ".pages.yaml"
        if yaml:
            root_content = yaml.safe_dump(
                root_data, sort_keys=False, default_flow_style=False
            )
        else:
            lines = [f"title: {root_data['title']}"]
            lines.append("nav:")
            for entry in root_nav_entries:
                lines.append(f"  - {entry}")
            root_content = "\n".join(lines) + "\n"

        if (
            not root_target.exists()
            or root_target.read_text(encoding="utf-8") != root_content
        ):
            root_target.write_text(root_content, encoding="utf-8")

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
