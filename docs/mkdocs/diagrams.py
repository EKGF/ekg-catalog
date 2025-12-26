"""PlantUML diagram generation."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .config import DIAGRAMS_SRC_DIR, USE_CASE_DIR


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
    if node_id == ".":
        base_name = "use-cases"
    else:
        base_name = Path(node_id).parts[-1] if Path(node_id).parts else node_id

    # Calculate depth: node_id parts + 1 (for the mindmap.puml being in a subdirectory)
    # e.g., "client-360" -> depth 2 (client-360/ + mindmap.puml) -> ../../include
    # e.g., "client-360/know-your-customer" -> depth 3 -> ../../../include
    # e.g., "." (root) -> depth 2 -> ../../include
    if node_id == ".":
        depth = 2
    else:
        depth = len(Path(node_id).parts) + 1
    prefix = "../" * depth
    lines = [
        f"@startmindmap {base_name}",
        "",
        f"!include {prefix}include/themes/light.puml",
        "",
    ]
    # Rule 2: Central node is boxed (use +[ for boxed node)
    lines.append(f"+[ [[ {make_link(node_id)} {title} ]]")

    # Rule 3: Left side shows only parents (no siblings)
    # If no parent, show nothing on left
    # Root node (.) should not show itself as parent
    if parents:
        for idx, parent_id in enumerate(parents):
            # Skip if parent is self (shouldn't happen, but safety check)
            if parent_id == node_id:
                continue
            parent = graph[parent_id]
            # Primary parent uses solid line, secondary parents use dotted line
            if idx == 0:
                connector = "--"  # solid line for primary parent
            else:
                connector = ".."  # dotted line for secondary parents
            parent_title = parent["title"]
            lines.append(f"{connector}_ [[ {make_link(parent_id)} {parent_title} ]]")

    # Rule 4: Right side shows children and grandchildren (but not great-grandchildren)
    # Rule 5: Sort alphabetically
    def get_children_and_grandchildren(node_id: str, graph: dict, max_depth: int = 2):
        """Get children and grandchildren up to max_depth levels."""
        result = []
        if max_depth <= 0:
            return result

        children = sorted(graph[node_id]["children"])
        for child_id in children:
            result.append((child_id, 1))  # (node_id, depth)
            if max_depth > 1:
                grandchildren = sorted(graph[child_id]["children"])
                for grandchild_id in grandchildren:
                    result.append((grandchild_id, 2))  # grandchildren at depth 2
        return result

    descendants = get_children_and_grandchildren(node_id, graph, max_depth=2)
    # Sort by depth first (children before grandchildren), then alphabetically by title
    descendants.sort(key=lambda x: (x[1], graph[x[0]]["title"]))

    for desc_id, depth in descendants:
        # Skip self (shouldn't happen, but safety check)
        if desc_id == node_id:
            continue
        desc_title = graph[desc_id]["title"]
        if depth == 1:
            # Direct children use ++_
            lines.append(f"++_ [[ {make_link(desc_id)} {desc_title} ]]")
        else:
            # Grandchildren use +++_ (one more + for deeper level)
            lines.append(f"+++_ [[ {make_link(desc_id)} {desc_title} ]]")

    lines.append("@endmindmap")
    return "\n".join(lines) + "\n"


def write_pumls(graph: dict, max_workers: int = 8):
    """Generate PlantUML mindmap files for all use cases."""
    # Collect expected targets (skip root node - no diagram needed)
    expected = set()
    for node_id in graph:
        if node_id == ".":
            continue  # Skip root node - no diagram needed
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
        if node_id == ".":
            return  # Skip root node - no diagram needed
        target = DIAGRAMS_SRC_DIR / node_id / "mindmap.puml"
        target.parent.mkdir(parents=True, exist_ok=True)
        content = puml_for_node(node_id, graph)
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                return
        target.write_text(content, encoding="utf-8")

    # Generate diagrams for all nodes except root
    node_ids_to_process = [node_id for node_id in graph.keys() if node_id != "."]
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        list(ex.map(render_and_write, node_ids_to_process))

    # Remove root diagram if it exists
    root_diagram = DIAGRAMS_SRC_DIR / "root" / "mindmap.puml"
    if root_diagram.exists():
        try:
            root_diagram.unlink()
        except Exception:
            pass
