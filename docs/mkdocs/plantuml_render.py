"""Parallel PlantUML rendering using the server API."""

import base64
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict

import httplib2

from .constants import DIAGRAMS_SRC_DIR

# Base64 encoding table for PlantUML
b64_to_plantuml = bytes.maketrans(
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
    b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_",
)


def encode_plantuml(content: str) -> str:
    """Encode PlantUML content to base64 format expected by server."""
    compressed = zlib.compress(content.encode("utf-8"))
    compressed_string = compressed[2:-4]  # Remove zlib header and checksum
    b64encoded = (
        base64.b64encode(compressed_string).translate(b64_to_plantuml).decode("utf-8")
    )
    return b64encoded


def render_diagram(
    puml_file: Path,
    output_file: Path,
    server_url: str,
    output_format: str = "svg",
    disable_ssl_validation: bool = False,
):
    """
    Render a single PlantUML diagram to SVG.

    Returns: (puml_file, success, error_message)
    """
    try:
        # Read and encode the PlantUML file
        content = puml_file.read_text(encoding="utf-8")
        encoded = encode_plantuml(content)

        # Build the URL
        url = f"{server_url}/{output_format}/{encoded}"

        # Make HTTP request
        http = httplib2.Http({})
        if disable_ssl_validation:
            http.disable_ssl_certificate_validation = True

        response, content = http.request(url)

        if response.status != 200:
            error_msg = f"HTTP {response.status}"
            if hasattr(response, "reason"):
                error_msg += f": {response.reason}"
            return (puml_file, False, error_msg)

        # Check if content is valid (SVG should start with <?xml or <svg)
        if not content or len(content) < 10:
            return (puml_file, False, "Empty response")

        # Write output file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(content)

        return (puml_file, True, "")
    except Exception as e:
        return (puml_file, False, str(e))


def render_diagrams_parallel(
    diagrams_dir: Path,
    output_dir: Path,
    server_url: str = "http://www.plantuml.com/plantuml",
    output_format: str = "svg",
    max_workers: int = 8,
    disable_ssl_validation: bool = False,
    pattern: str = "mindmap.puml",
) -> Dict[Path, tuple[bool, str]]:
    """
    Render all PlantUML diagrams in parallel.

    Args:
        pattern: Only render files matching this pattern (default: "mindmap.puml")

    Returns: Dict mapping puml_file -> (success, error_message)
    """
    # Find all matching .puml files
    if pattern:
        puml_files = [f for f in diagrams_dir.rglob("*.puml") if f.name == pattern]
    else:
        puml_files = list(diagrams_dir.rglob("*.puml"))

    if not puml_files:
        return {}

    # Prepare work items: (puml_file, output_file)
    # Match mkdocs-build-plantuml output structure: output_dir matches input structure
    work_items = []
    for puml_file in puml_files:
        rel_path = puml_file.relative_to(diagrams_dir)
        # Output structure: output_dir/rel_path.with_suffix(.svg)
        output_file = output_dir / rel_path.with_suffix(f".{output_format}")
        work_items.append((puml_file, output_file))

    # Render in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                render_diagram,
                puml_file,
                output_file,
                server_url,
                output_format,
                disable_ssl_validation,
            ): puml_file
            for puml_file, output_file in work_items
        }

        for future in as_completed(futures):
            puml_file, success, error = future.result()
            results[puml_file] = (success, error)

    return results
