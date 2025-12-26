import os
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any


try:
    import yaml
except ImportError:
    yaml = None


# -----------------------
# Existing macro (kept)
# -----------------------
def define_env(env):
    "Hook function"

    @env.macro
    def test123(page):
        pages = []
        while page.next_page:
            pages.append(page.next_page)
            page = page.next_page
        return pages

    def remove_h1(content):
        """Remove H1 tags from content for use case pages."""
        if not content:
            return content
        import re

        # Match H1 tags with any attributes, including headerlinks and newlines
        # Pattern: <h1[^>]*> ... </h1> where ... can include newlines and nested tags
        # Use DOTALL flag to make . match newlines, and MULTILINE for ^/$ behavior
        # Try multiple patterns to catch all variations
        h1_pattern = r"<h1[^>]*>.*?</h1>"
        result = re.sub(h1_pattern, "", content, flags=re.DOTALL | re.MULTILINE)
        # Also try pattern that matches across any whitespace
        h1_pattern2 = r"<h1[^>]*>[\s\S]*?</h1>"
        result = re.sub(h1_pattern2, "", result, flags=re.MULTILINE)
        # Clean up extra newlines that might be left
        result = re.sub(r"\n\s*\n\s*\n", "\n\n", result)
        return result

    # Register filter - try both methods for compatibility
    if hasattr(env, "filter"):
        try:
            env.filter("remove_h1")(remove_h1)
        except Exception:
            pass
    if hasattr(env, "filters"):
        env.filters["remove_h1"] = remove_h1
    # Also register as a macro for alternative access
    if hasattr(env, "macro"):
        try:
            env.macro("remove_h1")(remove_h1)
        except Exception:
            pass


# -----------------------
# HTML badge injection
# -----------------------
def on_page_content(html, page, config, files):
    """
    Inject objective letter badge before the first H1 heading.
    This runs after markdown is converted to HTML.
    Also remove H1 from use case pages since the template shows it.
    """
    # Remove H1 from use case pages (template will show it)
    if (
        hasattr(page, "url")
        and page.url
        and page.url.startswith("/use-case/")
        and page.url != "/use-case/"
    ):
        # Remove ALL H1 tags from content (template will show it at the top)
        # Pattern matches <h1>...</h1> even with newlines, whitespace, and headerlinks inside
        # Handle both single-line and multiline H1s
        # Use [\s\S] to match any character including newlines (more reliable than . with DOTALL)
        h1_pattern = r"<h1[^>]*>[\s\S]*?</h1>"
        html = re.sub(h1_pattern, "", html, flags=re.MULTILINE)
        # Also try with DOTALL flag as fallback
        h1_pattern2 = r"<h1[^>]*>.*?</h1>"
        html = re.sub(h1_pattern2, "", html, flags=re.DOTALL)
        # Clean up extra newlines that might be left after removing H1
        html = re.sub(r"\n\s*\n\s*\n+", "\n\n", html)

    # Check if page has letter_prefix in frontmatter
    if not hasattr(page, "meta") or "letter_prefix" not in page.meta:
        return html

    letter_prefix = page.meta["letter_prefix"]
    if not letter_prefix or not isinstance(letter_prefix, str):
        return html

    # Find the first H1 tag and wrap it with the badge
    # Pattern: <h1 ... > ... </h1>
    h1_pattern = r"(<h1[^>]*>)(.*?)(</h1>)"

    def replace_first_h1(match):
        opening_tag = match.group(1)
        h1_content = match.group(2)
        closing_tag = match.group(3)

        # Create the badge wrapper HTML
        badge_html = f'''<div class="objective-header-with-badge">
<span class="objective-badge-standalone" data-letter="{letter_prefix}"></span>

{opening_tag}{h1_content}{closing_tag}

</div>'''
        return badge_html

    # Replace only the first H1
    modified_html = re.sub(h1_pattern, replace_first_h1, html, count=1, flags=re.DOTALL)

    return modified_html


# -----------------------
# Use case graph + mindmap generation
# -----------------------
DOCS_DIR = Path(__file__).parent
USE_CASE_DIR = DOCS_DIR / "use-case"
DIAGRAMS_SRC_DIR = DOCS_DIR / "diagrams" / "src"

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "are",
    "was",
    "were",
    "will",
    "into",
    "across",
    "about",
    "your",
    "their",
    "they",
    "them",
    "can",
    "our",
    "you",
    "why",
    "how",
    "what",
    "when",
    "where",
    "who",
}


def _parse_frontmatter(text: str):
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


def _extract_title_and_description(body: str):
    title = None
    description = None
    lines = body.splitlines()
    # Title: first H1
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    # Description: first non-empty paragraph (not heading, not HTML tags)
    paragraph_lines = []
    for line in lines:
        if line.startswith("#"):
            if paragraph_lines:
                break
            continue
        stripped = line.strip()
        # Skip HTML tags (like <object>, <img>, etc.)
        if stripped.startswith("<") and stripped.endswith(">"):
            continue
        # Skip lines that are only HTML tags
        if re.match(r"^<[^>]+>$", stripped):
            continue
        if stripped:
            paragraph_lines.append(stripped)
        elif paragraph_lines:
            break
    if paragraph_lines:
        description = " ".join(paragraph_lines).strip()
    return title, description


def _extract_summary_section(body: str):
    """
    Extract the Summary section content and return (summary_text, body_without_summary).
    Summary section is everything between '## Summary' and the next heading (##).
    """
    lines = body.splitlines()
    summary_lines = []
    result_lines = []
    in_summary = False
    summary_started = False

    for line in lines:
        if line.strip() == "## Summary":
            in_summary = True
            summary_started = True
            # Don't include the heading in summary or result
            continue
        elif in_summary:
            if line.startswith("##"):
                # Next heading found, stop collecting summary
                in_summary = False
                result_lines.append(line)
            elif summary_started:
                summary_lines.append(line)
        else:
            result_lines.append(line)

    summary_text = "\n".join(summary_lines).strip()
    body_without_summary = "\n".join(result_lines).strip()

    return summary_text, body_without_summary


def _extract_proper_summary(body: str):
    """
    Extract a proper summary from the content.
    Priority:
    1. Summary section if it exists
    2. First paragraph from "Why EKG is Required" section
    3. First meaningful paragraph (skip "The Challenge" intro lines)
    """
    # Try Summary section first
    summary_text, _ = _extract_summary_section(body)
    if summary_text:
        return summary_text

    lines = body.splitlines()
    in_ekg_section = False
    paragraph_lines = []

    # Try to extract from "Why EKG is Required" section
    for line in lines:
        if line.strip() == "## Why EKG is Required":
            in_ekg_section = True
            continue
        elif in_ekg_section:
            if line.startswith("##"):
                # Next section found
                break
            stripped = line.strip()
            # Skip HTML tags
            if stripped.startswith("<") and stripped.endswith(">"):
                continue
            if re.match(r"^<[^>]+>$", stripped):
                continue
            # Skip bullet points (they're details, not summary)
            if stripped.startswith("- ") or stripped.startswith("* "):
                continue
            if stripped:
                paragraph_lines.append(stripped)
            elif paragraph_lines:
                # Got a paragraph
                break

    if paragraph_lines:
        return " ".join(paragraph_lines).strip()

    # Fallback: extract first meaningful paragraph (skip "The Challenge" intro)
    paragraph_lines = []
    skip_challenge_intro = True
    for line in lines:
        if line.startswith("#"):
            if line.startswith("## The Challenge"):
                skip_challenge_intro = True
                continue
            elif skip_challenge_intro and not line.startswith("##"):
                skip_challenge_intro = False
            if paragraph_lines:
                break
            continue
        stripped = line.strip()
        # Skip HTML tags
        if stripped.startswith("<") and stripped.endswith(">"):
            continue
        if re.match(r"^<[^>]+>$", stripped):
            continue
        # Skip bullet points in challenge section
        if skip_challenge_intro and (
            stripped.startswith("- ") or stripped.startswith("* ")
        ):
            continue
        if stripped:
            paragraph_lines.append(stripped)
        elif paragraph_lines:
            break

    if paragraph_lines:
        return " ".join(paragraph_lines).strip()

    return None


def _extract_keywords(title: str, description: str, limit: int = 12):
    text = f"{title or ''} {description or ''}"
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text)
    seen = set()
    keywords = []
    for w in words:
        lw = w.lower()
        if lw in STOPWORDS:
            continue
        if lw in seen:
            continue
        seen.add(lw)
        keywords.append(lw)
        if len(keywords) >= limit:
            break
    return keywords


def _resolve_parents(meta_parents, parent_dir: Path, self_dir: Path):
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


def _format_frontmatter(meta):
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


def _remove_diagram_tags(body: str) -> str:
    """Remove PlantUML diagram object tags from markdown body (diagrams are injected by template)."""
    lines = body.splitlines()
    filtered = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Remove <object> tags that reference diagrams/out/*.svg
        if line.startswith("<object") and "diagrams/out" in line and ".svg" in line:
            # Skip until closing </object> tag
            while i < len(lines) and "</object>" not in lines[i]:
                i += 1
            if i < len(lines) and "</object>" in lines[i]:
                i += 1
            continue
        filtered.append(lines[i])
        i += 1
    return "\n".join(filtered)


def _remove_h1_from_markdown(body: str) -> str:
    """Remove H1 headings (# Title) from markdown body for use case pages (template shows it)."""
    lines = body.splitlines()
    filtered = []
    for line in lines:
        # Skip lines that start with exactly one # followed by a space (H1 headings)
        if line.strip().startswith("# ") and not line.strip().startswith("##"):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def _update_frontmatter(path: Path, parent_dir: Path, self_dir: Path):
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    # Migrate old 'description' field to 'summary' if it exists
    if "description" in meta and "summary" not in meta:
        meta["summary"] = meta.pop("description")
    # Remove diagram tags (they're injected by template)
    body = _remove_diagram_tags(body)

    # Extract summary section and remove it from body if it exists
    summary_text, body_without_summary = _extract_summary_section(body)
    if summary_text:
        body = body_without_summary

    # Remove H1 headings from markdown body for use case pages (template will show it)
    # This prevents duplicate H1s in the rendered HTML
    body = _remove_h1_from_markdown(body)

    title_body, _ = _extract_title_and_description(body)

    title = meta.get("title") or title_body or path.stem.replace("-", " ").title()

    # Summary: frontmatter is leading, but extract if missing or incomplete
    summary = meta.get("summary")
    if not summary or len(summary) < 50 or summary.endswith(":"):
        # Extract proper summary from content
        summary = _extract_proper_summary(body)
        if not summary:
            raise ValueError(f"Missing 'summary' field in frontmatter for {path}")

    keywords = meta.get("keywords")
    if not keywords:
        keywords = _extract_keywords(title, summary)

    parents = meta.get("parents")
    # Default to [".."] if parents is None or empty list
    # All use cases should have parents: - .. (root-level ones reference use-case/index.md)
    # Handle both None and empty list cases
    if parents is None or (isinstance(parents, list) and len(parents) == 0):
        parents = [".."]
    resolved_parents = _resolve_parents(parents, parent_dir, self_dir)

    new_meta = {
        "title": title,
        "summary": summary,
        "keywords": keywords,
        "parents": parents,  # keep original expression (e.g., '..' or absolute)
    }
    new_front = _format_frontmatter(new_meta)
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


def _build_graph(max_workers: int = 8):
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
            data = _update_frontmatter(md_path, parent_dir, self_dir)
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
            if (
                Path(parent).parent == Path(node_id).parent
                and Path(parent) != Path(node_id).parent
            ):
                raise ValueError(f"Siblings cannot be parents: {parent} for {node_id}")
            nodes[parent]["children"].add(node_id)
    return nodes


def _primary_parent(graph: dict) -> Dict[str, str]:
    """Return mapping of node_id -> primary parent (first) or None."""
    mapping = {}
    for node_id, info in graph.items():
        mapping[node_id] = info["parents"][0] if info["parents"] else None
    return mapping


def _build_nav(node_id: str, graph: dict, primary: dict) -> List[Any]:
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


def _write_pages_yaml(graph: dict):
    """Generate .pages.yaml for every directory that has an index.md use case."""
    primary = _primary_parent(graph)

    def write_for(node_id: str):
        node = graph[node_id]
        if node["path"].stem != "index":
            return
        dir_path = node["path"].parent
        nav_entries = _build_nav(node_id, graph, primary)
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


def _make_link(rel_path: str):
    rel = rel_path.strip("/")
    return f"/use-case/{rel}/" if rel else "/use-case/"


def _puml_for_node(node_id: str, graph: dict):
    node = graph[node_id]
    title = node["title"]
    parents = node["parents"]
    children = sorted(node["children"])

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
    lines.append(f"+ [[ {_make_link(node_id)} {title} ]]")

    # Parents on the left with their children
    if parents:
        for idx, parent_id in enumerate(parents):
            parent = graph[parent_id]
            connector = "--"  # mindmap left branch
            label = parent["title"]
            if idx > 0:
                label = f"{label} (secondary)"
            lines.append(f"{connector}_ [[ {_make_link(parent_id)} {label} ]]")
            siblings = sorted(child for child in parent["children"] if child != node_id)
            for sib in siblings:
                sib_title = graph[sib]["title"]
                lines.append(f"---_ [[ {_make_link(sib)} {sib_title} ]]")

    # Children on the right
    for child_id in children:
        child_title = graph[child_id]["title"]
        lines.append(f"++_ [[ {_make_link(child_id)} {child_title} ]]")

    lines.append("@endmindmap")
    return "\n".join(lines) + "\n"


def _write_pumls(graph: dict, max_workers: int = 8):
    # Collect expected targets
    expected = set()
    for node_id in graph:
        if node_id == ".":
            target = DIAGRAMS_SRC_DIR / "root" / "mindmap.puml"
        else:
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
            target = DIAGRAMS_SRC_DIR / "root" / "mindmap.puml"
        else:
            target = DIAGRAMS_SRC_DIR / node_id / "mindmap.puml"
        target.parent.mkdir(parents=True, exist_ok=True)
        content = _puml_for_node(node_id, graph)
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == content:
                return
        target.write_text(content, encoding="utf-8")

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        list(ex.map(render_and_write, graph.keys()))


def on_pre_build(config):
    """
    MkDocs hook: normalize use case metadata and generate mindmaps.
    """
    graph = _build_graph()
    _write_pumls(graph)
    _write_pages_yaml(graph)


if __name__ == "__main__":
    # Allow running the script directly to update frontmatter
    on_pre_build(None)
