"""PlantUML diagram generation."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .constants import DIAGRAMS_SRC_DIR, USE_CASE_DIR


def make_link(rel_path: str):
    """Generate a link path for a use case."""
    rel = rel_path.strip("/")
    return f"/use-case/{rel}/" if rel else "/use-case/"


def puml_for_node(node_id: str, graph: dict):
    """Generate PlantUML mindmap content for a node."""
    node = graph[node_id]
    title = node["title"]
    parents = node["parents"]

    # Extract base name for @startmindmap directive
    base_name = Path(node_id).parts[-1] if Path(node_id).parts else node_id

    # Calculate depth: node_id parts + 1 (for the mindmap.puml being in a subdirectory)
    # e.g., "client-360" -> depth 2 (client-360/ + mindmap.puml) -> ../../include
    # e.g., "client-360/know-your-customer" -> depth 3 -> ../../../include
    depth = len(Path(node_id).parts) + 1
    prefix = "../" * depth
    lines = [
        f"@startmindmap {base_name}",
        "",
        f"!include {prefix}include/themes/light.puml",
        "",
    ]

    # Rule 2: Central node is boxed - must come FIRST
    lines.append(f"+{title}")

    # Rule 3: Left side shows parents and grandparents
    # Rule 6: Top-level use cases (direct subdirectories of docs/use-case) are root nodes
    # and should never show a parent to the left
    # If no parent, show nothing on left
    # IMPORTANT: In PlantUML mindmaps, left-side nodes come AFTER the center node
    # Use - (dash) for left side: -- for parent (closer), --- for grandparent (farther)
    is_top_level = len(Path(node_id).parts) == 1
    if parents and not is_top_level:
        # Collect all ancestors to show (parents and grandparents)
        ancestors_to_show = []

        # First, add all parents
        for idx, parent_id in enumerate(parents):
            # Skip empty parent (excluded from graph per Rule 6) and self (shouldn't happen)
            if not parent_id or parent_id == "" or parent_id == node_id:
                continue
            if parent_id not in graph:
                continue
            parent = graph[parent_id]
            # Primary parent uses solid line, secondary parents use dotted line
            is_primary = idx == 0
            ancestors_to_show.append((parent_id, parent["title"], is_primary, False))

            # Add grandparent(s) of primary parent only
            # This shows 2 ancestor levels: parent and grandparent
            if is_primary and parent["parents"]:
                for grandparent_id in parent["parents"]:
                    # Skip empty parent and self
                    if (
                        not grandparent_id
                        or grandparent_id == ""
                        or grandparent_id == node_id
                        or grandparent_id == parent_id
                    ):
                        continue
                    if grandparent_id not in graph:
                        continue
                    grandparent = graph[grandparent_id]
                    # Add grandparent (marked as level 2)
                    ancestors_to_show.append(
                        (grandparent_id, grandparent["title"], False, 2)
                    )

        # Separate ancestors by level
        # Level 1 = parent (False), Level 2 = grandparent
        grandparents = [
            (pid, title) for pid, title, _, level in ancestors_to_show if level == 2
        ]
        parents_list = [
            (pid, title, is_primary)
            for pid, title, is_primary, level in ancestors_to_show
            if level == False  # Parents are marked as False (not a level number)
        ]

        # Render left-side ancestors AFTER the center node
        # Use - (dash) with _ (underscore): --- for grandparent (farther), -- for parent (closer)
        # The _ removes the border/box
        # In PlantUML mindmaps: MORE dashes = farther from center
        # Order: parent first, siblings (nested under parent), then grandparent

        # Parents first (closer to center, 2 dashes)
        for parent_id, parent_title, is_primary in parents_list:
            lines.append(f"--_ [[{make_link(parent_id)} {parent_title}]]")

        # Then grandparents (farther from center, 3 dashes)
        for grandparent_id, grandparent_title in grandparents:
            lines.append(f"---_ [[{make_link(grandparent_id)} {grandparent_title}]]")

    # Rule 4: Right side shows children and grandchildren (but not great-grandchildren)
    # Rule 5: Sort alphabetically
    # In PlantUML mindmaps, grandchildren must be nested under their parent children
    # to avoid them all attaching to the last child node
    children = sorted(graph[node_id]["children"])
    for child_id in children:
        # Skip self (shouldn't happen, but safety check)
        if child_id == node_id:
            continue
        child_title = graph[child_id]["title"]
        # Direct children use ++_
        lines.append(f"++_ [[{make_link(child_id)} {child_title}]]")

        # Add grandchildren immediately after their parent (nested)
        grandchildren = sorted(graph[child_id]["children"])
        for grandchild_id in grandchildren:
            # Skip self (shouldn't happen, but safety check)
            if grandchild_id == node_id:
                continue
            grandchild_title = graph[grandchild_id]["title"]
            # Grandchildren use +++_ (one more + for deeper level)
            lines.append(f"+++_ [[{make_link(grandchild_id)} {grandchild_title}]]")

    lines.append("@endmindmap")
    return "\n".join(lines) + "\n"


def write_pumls(graph: dict, max_workers: int = 8):
    """Generate PlantUML mindmap files for all use cases."""
    # Collect expected targets
    expected = set()
    for node_id in graph:
        target = DIAGRAMS_SRC_DIR / node_id / "mindmap.puml"
        expected.add(target.resolve())

    # Remove stale generated mindmaps that no longer map to an existing use case
    for puml in DIAGRAMS_SRC_DIR.rglob("mindmap.puml"):
        rel = puml.parent.relative_to(DIAGRAMS_SRC_DIR)
        if rel == Path("root"):
            continue
        candidate = USE_CASE_DIR / rel / "index.md"
        if not candidate.exists() and puml.resolve() not in expected:
            try:
                puml.unlink()
            except Exception:
                pass

    # Also remove old .puml files that are not mindmap.puml (migration cleanup)
    for puml in DIAGRAMS_SRC_DIR.rglob("*.puml"):
        if puml.name != "mindmap.puml":
            rel = puml.relative_to(DIAGRAMS_SRC_DIR).with_suffix("")
            if rel == Path("root"):
                continue
            candidate = USE_CASE_DIR / rel / "index.md"
            if candidate.exists():
                # This is an old format file, remove it
                try:
                    puml.unlink()
                except Exception:
                    pass

    def render_and_write(node_id: str):
        target = DIAGRAMS_SRC_DIR / node_id / "mindmap.puml"
        target.parent.mkdir(parents=True, exist_ok=True)
        content = puml_for_node(node_id, graph)
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                return
        target.write_text(content, encoding="utf-8")

    # Generate diagrams for all nodes in the graph
    # (Root node is excluded during graph building per Rule 6)
    node_ids_to_process = list(graph.keys())
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        list(ex.map(render_and_write, node_ids_to_process))

    # Clean up any root node diagram that might exist (should not be generated per Rule 6)
    root_diagram = DIAGRAMS_SRC_DIR / "mindmap.puml"
    if root_diagram.exists():
        try:
            root_diagram.unlink()
        except Exception:
            pass
