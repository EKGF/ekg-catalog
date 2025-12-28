"""MkDocs hooks."""

import re

# Use relative imports - MkDocs imports this as a module
from .graph import build_graph
from .navigation import write_pages_yaml
from .svg_generator import generate_svg_use_case_trees


def define_env(env):
    """MkDocs hook: define macros and filters."""

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
        # Use DOTALL flag to make . match newlines, and MULTILINE for ^/$ behavior
        # Try multiple patterns to ensure we catch all variations
        h1_pattern1 = r"<h1[^>]*>[\s\S]*?</h1>"
        html = re.sub(h1_pattern1, "", html, flags=re.MULTILINE)
        # Pattern 2: Match H1 with DOTALL flag (makes . match newlines)
        h1_pattern2 = r"<h1[^>]*>.*?</h1>"
        html = re.sub(h1_pattern2, "", html, flags=re.DOTALL)
        # Pattern 3: More aggressive - match across any whitespace
        h1_pattern3 = r"<h1[^>]*>\s*[\s\S]*?\s*</h1>"
        html = re.sub(h1_pattern3, "", html, flags=re.MULTILINE)
        # Clean up extra newlines that might be left after removing H1
        html = re.sub(r"\n\s*\n\s*\n+", "\n\n", html)

    # Check if page has letter_prefix in frontmatter
    if not hasattr(page, "meta") or "letter_prefix" not in page.meta:
        return html

    letter_prefix = page.meta["letter_prefix"]
    if not letter_prefix or not isinstance(letter_prefix, str):
        return html

    # Find the first H1 tag
    h1_match = re.search(r"<h1[^>]*>.*?</h1>", html, re.DOTALL | re.MULTILINE)
    if not h1_match:
        return html

    # Extract the H1 content
    h1_content = h1_match.group(0)

    # Create the badge HTML
    badge_html = f'<div class="objective-header-with-badge"><span class="objective-badge-standalone" data-letter="{letter_prefix}"></span>{h1_content}</div>'

    # Replace the H1 with the badge + H1
    modified_html = html[: h1_match.start()] + badge_html + html[h1_match.end() :]

    return modified_html


def on_pre_build(config):
    """
    MkDocs hook: normalize use case metadata and generate mindmaps.
    """
    import time
    from pathlib import Path

    start = time.time()
    graph = build_graph()
    graph_time = time.time() - start

    start = time.time()
    generate_svg_use_case_trees(graph)
    svg_time = time.time() - start

    start = time.time()
    write_pages_yaml(graph)
    nav_time = time.time() - start

    # Count generated SVG diagrams
    from .constants import DIAGRAMS_SRC_DIR

    svg_count = (
        len(list(DIAGRAMS_SRC_DIR.rglob("use-case-tree.svg")))
        if DIAGRAMS_SRC_DIR.exists()
        else 0
    )

    total_time = graph_time + svg_time + nav_time
    print(
        f"SVG generation timing: graph={graph_time:.3f}s ({len(graph)} nodes), "
        f"svg={svg_time:.3f}s ({svg_count} files), "
        f"navigation={nav_time:.3f}s"
    )
    if svg_count > 0:
        print(f"  Average: {svg_time / svg_count * 1000:.2f} ms per SVG")
    print(f"  Total: {total_time:.3f}s")
