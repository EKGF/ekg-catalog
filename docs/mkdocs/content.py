"""Content extraction and cleaning utilities."""

import re
from .config import STOP_WORDS


def extract_title_and_description(body: str):
    """Extract title (first H1) and description (first paragraph) from markdown body."""
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


def extract_summary_section(body: str):
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


def extract_proper_summary(body: str):
    """
    Extract a proper summary from the content.
    Priority:
    1. Summary section if it exists
    2. First paragraph from "Why EKG is Required" section
    3. First meaningful paragraph (skip "The Challenge" intro lines)
    """
    # Try Summary section first
    summary_text, _ = extract_summary_section(body)
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


def extract_keywords(title: str, description: str, limit: int = 12):
    """Extract keywords from title and description, excluding stop words."""
    text = f"{title or ''} {description or ''}"
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text)
    seen = set()
    keywords = []
    for w in words:
        lw = w.lower()
        if lw in STOP_WORDS:
            continue
        if lw in seen:
            continue
        seen.add(lw)
        keywords.append(lw)
        if len(keywords) >= limit:
            break
    return keywords


def remove_diagram_tags(body: str) -> str:
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


def remove_h1_from_markdown(body: str) -> str:
    """Remove H1 headings (# Title) from markdown body for use case pages (template shows it)."""
    lines = body.splitlines()
    filtered = []
    for line in lines:
        # Skip lines that start with exactly one # followed by a space (H1 headings)
        if line.strip().startswith("# ") and not line.strip().startswith("##"):
            continue
        filtered.append(line)
    return "\n".join(filtered)
