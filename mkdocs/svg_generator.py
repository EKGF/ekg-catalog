"""Direct SVG use case tree diagram generator."""

from pathlib import Path
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from .constants import DIAGRAMS_SRC_DIR


class SVGUseCaseTreeGenerator:
    """Generate SVG use case tree diagrams directly."""

    def __init__(self, theme="light"):
        self.theme = theme
        # Theme colors
        if theme == "dark":
            self.bg_color = "transparent"
            self.box_fill = "#4051B5"
            self.box_stroke = "#FF6F00"
            self.text_color = "#FFFFFF"
            self.link_color = "#90EE90"  # Light green for dark mode
            self.line_color = "#FF9900"
        else:  # light
            self.bg_color = "transparent"
            self.box_fill = "#4051B5"
            self.box_stroke = "#FF6F00"
            self.text_color = "#FFFFFF"
            self.link_color = "#4051B5"
            self.line_color = "#FF6F00"

        # Layout constants
        self.node_height = 25
        self.node_padding_x = 10
        self.node_padding_y = 5
        self.vertical_spacing = 0
        self.h_spacing = 50
        self.box_radius = 4
        self.font_size = 13
        self.font_family = "Roboto, sans-serif"

    def make_link(self, rel_path: str) -> str:
        """Generate a link path for a use case."""
        rel = rel_path.strip("/")
        return f"/use-case/{rel}/" if rel else "/use-case/"

    def _calculate_node_width(self, text: str, is_bold: bool = False) -> float:
        """
        Calculate the precise width needed for a text string using Pillow and Roboto.
        Checks multiple system paths for cross-platform compatibility (macOS/Linux).
        """
        from PIL import ImageFont
        import os

        font_name = "Roboto-Bold.ttf" if is_bold else "Roboto-Regular.ttf"
        # Standard search paths for macOS and Linux (including Github Actions)
        possible_paths = [
            os.path.expanduser(f"~/Library/Fonts/{font_name}"),
            f"/Library/Fonts/{font_name}",
            f"/System/Library/Fonts/{font_name}",
            f"/usr/share/fonts/truetype/roboto/{font_name}",
            f"/usr/share/fonts/truetype/liberation/{font_name.replace('Roboto', 'LiberationSans')}",
        ]

        font_path = next((p for p in possible_paths if os.path.exists(p)), None)

        try:
            # Use the actual font file for pixel-perfect measurement
            font = (
                ImageFont.truetype(font_path, self.font_size)
                if font_path
                else ImageFont.load_default()
            )
            width = font.getlength(text)
        except Exception:
            # Fallback to precise weighted estimation if font loading fails
            width = 0
            multiplier = 1.2 if is_bold else 1.0
            for char in text:
                if char.isupper():
                    width += 8.5 * multiplier
                elif char in "mwMW@&":
                    width += 11.5 * multiplier
                elif char in "ijlftI1!|.,;:'\" ":
                    width += 3.0 * multiplier
                elif char in "abcdeghknopqrsuvxyz023456789$-+":
                    width += 6.5 * multiplier
                else:
                    width += 7.0 * multiplier

        return width + 2 * self.node_padding_x

    def calculate_layout(
        self, node_id: str, graph: dict
    ) -> Tuple[
        Dict[str, Tuple[float, float]],
        Dict[str, str],
        Dict[str, float],
        List[Tuple[str, str]],
    ]:
        """Calculate positions using global column packing."""
        positions = {}
        node_types = {}
        node_widths = {}
        edges = []
        node = graph[node_id]

        def calc_width(nid, is_center=False):
            if nid in graph and nid not in node_widths:
                node_widths[nid] = self._calculate_node_width(
                    graph[nid]["title"], is_bold=is_center
                )

        # 1. Collect nodes for each column
        parents = node.get("parents", [])
        primary_parent_id = next(
            (p for p in parents if p and p != "" and p in graph), None
        )

        level_0 = (
            sorted(list(graph[primary_parent_id]["children"]))
            if primary_parent_id
            else [node_id]
        )
        level_r1 = sorted(list(graph[node_id]["children"]))
        level_r2 = []
        for r1id in level_r1:
            level_r2.extend(sorted(list(graph[r1id]["children"])))
        level_l1 = [primary_parent_id] if primary_parent_id else []
        level_l2 = []
        if primary_parent_id and graph[primary_parent_id].get("parents"):
            gp_id = next(
                (
                    p
                    for p in graph[primary_parent_id]["parents"]
                    if p and p != "" and p in graph
                ),
                None,
            )
            if gp_id:
                level_l2 = [gp_id]

        # Calculate all widths
        calc_width(node_id, is_center=True)
        for nid in level_l2 + level_l1 + level_0 + level_r1 + level_r2:
            calc_width(nid, is_center=(nid == node_id))

        # 2. Determine x-positions
        col_0_x = 400
        max_col_0_w = max(node_widths[nid] for nid in level_0)
        col_r1_x = col_0_x + max_col_0_w + self.h_spacing
        max_col_r1_w = max([node_widths[nid] for nid in level_r1] + [0])
        col_r2_x = col_r1_x + max_col_r1_w + self.h_spacing
        max_col_l1_w = max([node_widths[nid] for nid in level_l1] + [0])
        col_l1_x = col_0_x - self.h_spacing - max_col_l1_w
        max_col_l2_w = max([node_widths[nid] for nid in level_l2] + [0])
        col_l2_x = col_l1_x - self.h_spacing - max_col_l2_w

        # 3. Position nodes tightly in columns (Y centering around 400)
        def _position_column(nids, x, type_name):
            if not nids:
                return
            total_h = len(nids) * self.node_height
            start_y = 400 - total_h / 2 + self.node_height / 2
            for i, nid in enumerate(nids):
                positions[nid] = (x, start_y + i * self.node_height)
                node_types[nid] = type_name

        _position_column(level_0, col_0_x, "sibling")
        node_types[node_id] = "center"
        _position_column(level_r1, col_r1_x, "child")
        _position_column(level_r2, col_r2_x, "grandchild")

        center_y = positions[node_id][1]
        if level_l1:
            positions[level_l1[0]] = (col_l1_x, center_y)
            node_types[level_l1[0]] = "parent"
        if level_l2:
            positions[level_l2[0]] = (col_l2_x, center_y)
            node_types[level_l2[0]] = "grandparent"

        # 4. Build edges
        if primary_parent_id:
            for nid in level_0:
                edges.append((primary_parent_id, nid))
            if level_l2:
                edges.append((level_l2[0], primary_parent_id))
        for nid in level_r1:
            edges.append((node_id, nid))
            # Sort children for deterministic SVG output
            for gcid in sorted(list(graph[nid].get("children", []))):
                if gcid in positions:
                    edges.append((nid, gcid))

        return positions, node_types, node_widths, edges

    def generate_svg(
        self,
        node_id: str,
        graph: dict,
        positions: Dict[str, Tuple[float, float]],
        node_types: Dict[str, str],
        node_widths: Dict[str, float],
        edges: List[Tuple[str, str]],
    ) -> str:
        """Generate SVG content for a use case tree diagram."""
        all_x_left = [x for x, y in positions.values()]
        all_x_right = [x + node_widths[nid] for nid, (x, y) in positions.items()]
        all_y = [y for x, y in positions.values()]

        # Use minimal padding (5px) for a tight fit
        padding = 5
        min_x = min(all_x_left) - padding
        min_y = min(all_y) - (self.node_height / 2) - padding
        max_x = max(all_x_right) + padding
        max_y = max(all_y) + (self.node_height / 2) + padding
        width, height = max_x - min_x, max_y - min_y

        # Pre-calculate max_x2 for each column group to determine common trunk points
        col_max_x2 = {}
        # Use sorted keys for deterministic calculation
        for nid in sorted(positions.keys()):
            x, y = positions[nid]
            ntype = node_types[nid]
            if ntype in ["center", "sibling"]:
                col = "level0"
            elif ntype == "parent":
                col = "levelL1"
            elif ntype == "grandparent":
                col = "levelL2"
            else:
                col = ntype
            col_max_x2[col] = max(col_max_x2.get(col, 0), x + node_widths[nid])

        svg = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
                "viewBox": f"{min_x:.2f} {min_y:.2f} {width:.2f} {height:.2f}",
                "width": f"{width:.2f}px",
                "height": f"{height:.2f}px",
                "class": "use-case-tree-svg",
            },
        )
        ET.SubElement(
            svg, "rect", {"width": "100%", "height": "100%", "fill": self.bg_color}
        )

        # Sort edges for deterministic XML element order
        for parent_id, child_id in sorted(edges):
            if parent_id not in positions or child_id not in positions:
                continue
            p_x, p_y = positions[parent_id]
            c_x, c_y = positions[child_id]
            p_w, c_w = node_widths[parent_id], node_widths[child_id]
            p_type = node_types[parent_id]

            if c_x > p_x:
                # Group columns together for trunk calculation
                if p_type in ["center", "sibling"]:
                    col = "level0"
                elif p_type == "parent":
                    col = "levelL1"
                elif p_type == "grandparent":
                    col = "levelL2"
                else:
                    col = p_type

                # Determine if this is the absolute leftmost column in the diagram
                is_leftmost = (p_type == "grandparent") or (
                    p_type == "parent" and "levelL2" not in col_max_x2
                )

                # Trunk offset: +10px for the leftmost column (sticks out), -5px for all others (tight but safe)
                offset = 10 if is_leftmost else -5
                trunk_x = col_max_x2.get(col, p_x + p_w) + offset

                # Draw straight line from parent edge to trunk
                p_edge_x = p_x + p_w
                if trunk_x > p_edge_x:
                    ET.SubElement(
                        svg,
                        "line",
                        {
                            "x1": f"{p_edge_x:.2f}",
                            "y1": f"{p_y:.2f}",
                            "x2": f"{trunk_x:.2f}",
                            "y2": f"{p_y:.2f}",
                            "stroke": self.line_color,
                            "stroke-width": "1.5",
                        },
                    )

                self._draw_connection(
                    svg, trunk_x, p_y, c_x, c_y, node_types.get(child_id, "")
                )
            else:
                self._draw_connection(
                    svg, p_x, p_y, c_x + c_w, c_y, node_types.get(child_id, "")
                )

        # Draw nodes (positions are left edges)
        # Use sorted keys for deterministic XML element order
        for nid in sorted(positions.keys()):
            box_left, y = positions[nid]
            self._draw_node(
                svg,
                nid,
                graph[nid]["title"],
                box_left,
                y,
                node_widths[nid],
                nid == node_id,
            )

        ET.indent(svg, space="  ")
        return ET.tostring(svg, encoding="unicode")

    def _draw_connection(
        self,
        parent: ET.Element,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        node_type: str,
    ):
        """Draw a curved connection line using Bezier curves."""
        dx, dy = x2 - x1, y2 - y1
        control_offset = abs(dx) * 0.45
        if dx > 0:
            cx1, cy1, cx2, cy2 = x1 + control_offset, y1, x2 - control_offset, y2
        else:
            cx1, cy1, cx2, cy2 = x1 - control_offset, y1, x2 + control_offset, y2
        path_data = f"M {x1:.2f} {y1:.2f} C {cx1:.2f} {cy1:.2f}, {cx2:.2f} {cy2:.2f}, {x2:.2f} {y2:.2f}"
        ET.SubElement(
            parent,
            "path",
            {
                "d": path_data,
                "stroke": self.line_color,
                "stroke-width": "1.5",
                "fill": "none",
            },
        )

    def _draw_node(
        self,
        parent: ET.Element,
        node_id: str,
        title: str,
        box_left: float,
        y: float,
        node_width: float,
        is_center: bool,
    ):
        """Draw a single node (box + text). box_left is the LEFT EDGE of the box."""
        box_x, box_y = box_left, y - self.node_height / 2

        # Link wraps both the rectangle and the text for a larger clickable area
        link = self.make_link(node_id)
        a = ET.SubElement(parent, "a", {"xlink:href": link, "target": "_top"})

        if is_center:
            ET.SubElement(
                a,
                "rect",
                {
                    "x": f"{box_x:.2f}",
                    "y": f"{box_y:.2f}",
                    "width": f"{node_width:.2f}",
                    "height": str(self.node_height),
                    "rx": str(self.box_radius),
                    "ry": str(self.box_radius),
                    "fill": self.box_fill,
                    "stroke": self.box_stroke,
                    "stroke-width": "1.5",
                },
            )
        else:
            ET.SubElement(
                a,
                "rect",
                {
                    "x": f"{box_x:.2f}",
                    "y": f"{box_y:.2f}",
                    "width": f"{node_width:.2f}",
                    "height": str(self.node_height),
                    "rx": str(self.box_radius),
                    "ry": str(self.box_radius),
                    "fill": "none",
                    "stroke": "none",
                    "pointer-events": "all",
                },
            )

        text_x, text_y = box_x + self.node_padding_x, y + 4.5
        ET.SubElement(
            a,
            "text",
            {
                "x": f"{text_x:.2f}",
                "y": f"{text_y:.2f}",
                "text-anchor": "start",
                "font-family": self.font_family,
                "font-size": str(self.font_size),
                "fill": self.text_color if is_center else self.link_color,
                "font-weight": "bold" if is_center else "normal",
            },
        ).text = title


try:
    import mkdocs_gen_files
except ImportError:
    mkdocs_gen_files = None


def generate_svg_use_case_trees(graph: dict, max_workers: int = 8):
    """Generate SVG use case tree diagram files for all use cases."""

    def render_and_write(node_id: str):
        # Generate both light and dark versions
        for theme in ["light", "dark"]:
            generator = SVGUseCaseTreeGenerator(theme=theme)
            positions, node_types, node_widths, edges = generator.calculate_layout(
                node_id, graph
            )
            svg_content = generator.generate_svg(
                node_id, graph, positions, node_types, node_widths, edges
            )

            suffix = "_dark" if theme == "dark" else ""
            path = f"use-case-tree-diagrams/{node_id}/use-case-tree{suffix}.svg"

            if mkdocs_gen_files:
                # Use mkdocs-gen-files to avoid triggering watch loop
                # This writes to a virtual file system during serve/build
                with mkdocs_gen_files.open(path, "wb") as f:
                    f.write(svg_content.encode("utf-8"))
            else:
                # Fallback to direct file writing
                target = DIAGRAMS_SRC_DIR / node_id / f"use-case-tree{suffix}.svg"

                if target.exists():
                    existing = target.read_text(encoding="utf-8")
                    if existing == svg_content:
                        continue

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(svg_content, encoding="utf-8")

    # Generate diagrams for all nodes in the graph
    # Sort node IDs for deterministic build order
    node_ids_to_process = sorted(list(graph.keys()))

    if mkdocs_gen_files:
        # Use mkdocs-gen-files sequentially to avoid potential thread-safety issues
        # with the plugin's virtual file system
        for node_id in node_ids_to_process:
            render_and_write(node_id)
    else:
        # Fallback to parallel direct file writing
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            list(ex.map(render_and_write, node_ids_to_process))
