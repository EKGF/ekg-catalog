"""Async PlantUML rendering plugin with parallel HTTP requests."""

import asyncio
import base64
import re
import string
import zlib
from pathlib import Path
from typing import Dict, List, Optional

import httpx

# Import mkdocs modules - must be done before our local modules are imported
# to avoid shadowing issues with docs/mkdocs/config.py (now constants.py)
from mkdocs.config import config_options, base
from mkdocs.plugins import BasePlugin

# PlantUML encoding table
plantuml_alphabet = (
    string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
)
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
b64_to_plantuml = bytes.maketrans(
    base64_alphabet.encode("utf-8"), plantuml_alphabet.encode("utf-8")
)


class AsyncPlantUMLPluginConfig(base.Config):
    """Configuration for async PlantUML plugin."""

    render = config_options.Type(str, default="server")
    server = config_options.Type(str, default="http://www.plantuml.com/plantuml")
    disable_ssl_certificate_validation = config_options.Type(bool, default=False)
    output_format = config_options.Type(str, default="svg")
    diagram_root = config_options.Type(str, default="docs/diagrams")
    output_folder = config_options.Type(str, default="out")
    input_folder = config_options.Type(str, default="src")
    input_extensions = config_options.Type(str, default="")
    theme_enabled = config_options.Type(bool, default=False)
    theme_folder = config_options.Type(str, default="include/themes/")
    theme_light = config_options.Type(str, default="light.puml")
    theme_dark = config_options.Type(str, default="dark.puml")
    max_concurrent_requests = config_options.Type(int, default=8)


class Diagram:
    """Represents a PlantUML diagram to be rendered."""

    def __init__(self, file: Path, directory: Path, root_dir: Path, out_dir: Path):
        self.file = file
        self.directory = directory
        self.root_dir = root_dir
        self.out_dir = out_dir
        self.src_file_lines: List[str] = []
        self.out_file = ""
        self.out_file_dark = ""
        self.b64encoded = ""
        self.b64encoded_dark = ""
        self.src_time = 0
        self.img_time = 0
        self.img_time_dark = 0
        self.inc_time = 0


class AsyncPlantUMLPlugin(BasePlugin[AsyncPlantUMLPluginConfig]):
    """Async PlantUML plugin with parallel rendering."""

    def __init__(self):
        self.diagrams: List[Diagram] = []

    def on_pre_build(self, config):
        """Discover diagrams and render them in parallel."""
        import time

        start = time.time()

        # Discover diagrams
        diagrams = self._discover_diagrams()
        if not diagrams:
            return config

        # Process includes and encode (can be done in parallel per diagram)
        self._process_diagrams(diagrams)

        # Render in parallel using async HTTP
        asyncio.run(self._render_all_async(diagrams))

        elapsed = time.time() - start
        print(f"Async PlantUML rendering: {len(diagrams)} diagrams in {elapsed:.2f}s")
        if len(diagrams) > 0:
            print(f"  Average: {elapsed / len(diagrams) * 1000:.2f} ms per diagram")

        return config

    def _discover_diagrams(self) -> List[Diagram]:
        """Discover all PlantUML files to render."""
        diagrams = []
        diagram_root = Path(self.config["diagram_root"])
        src_dir = diagram_root / self.config["input_folder"]
        out_dir = diagram_root / self.config["output_folder"]

        if not src_dir.exists():
            return diagrams

        for puml_file in src_dir.rglob("*.puml"):
            if not self._file_matches_extension(puml_file.name):
                continue

            # Skip root node diagram (per Rule 6: there is no single root node)
            # Root diagram would be at src_dir / "mindmap.puml" (no subdirectory)
            # Each top-level use case is a root node itself and has its own diagram
            if puml_file.parent == src_dir and puml_file.name == "mindmap.puml":
                continue

            rel_path = puml_file.relative_to(src_dir)
            diagram = Diagram(
                file=puml_file.name,
                directory=puml_file.parent,
                root_dir=diagram_root,
                out_dir=out_dir / rel_path.parent,
            )
            diagram.src_file_lines = puml_file.read_text(encoding="utf-8").splitlines(
                keepends=True
            )
            diagram.src_time = puml_file.stat().st_mtime

            # Determine output filename
            diagram.out_file = f"{puml_file.stem}.{self.config['output_format']}"
            if self.config["theme_enabled"]:
                diagram.out_file_dark = (
                    f"{puml_file.stem}_dark.{self.config['output_format']}"
                )

            diagrams.append(diagram)

        return diagrams

    def _file_matches_extension(self, filename: str) -> bool:
        """Check if file matches configured extensions."""
        if not self.config["input_extensions"]:
            return True
        extensions = self.config["input_extensions"].split(",")
        return any(filename.endswith(ext) for ext in extensions)

    def _process_diagrams(self, diagrams: List[Diagram]):
        """Process includes and encode diagrams."""
        for diagram in diagrams:
            # Process includes for light mode
            content = self._read_file_recursive(
                diagram.src_file_lines,
                diagram,
                diagram.directory,
                dark_mode=False,
            )
            diagram.b64encoded = self._encode_plantuml(content)

            # Process includes for dark mode if enabled
            if self.config["theme_enabled"]:
                content_dark = self._read_file_recursive(
                    diagram.src_file_lines,
                    diagram,
                    diagram.directory,
                    dark_mode=True,
                )
                diagram.b64encoded_dark = self._encode_plantuml(content_dark)

    def _read_file_recursive(
        self,
        lines: List[str],
        diagram: Diagram,
        directory: Path,
        dark_mode: bool,
    ) -> str:
        """Recursively read file and process includes."""
        temp_file = ""
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("!include"):
                temp_file = self._process_include_line(
                    diagram, line, temp_file, directory, dark_mode
                )
            else:
                # Preserve original line including newline
                temp_file += line
                # If line doesn't end with newline, add one
                if not line.endswith("\n"):
                    temp_file += "\n"
        return temp_file

    def _process_include_line(
        self,
        diagram: Diagram,
        line: str,
        temp_file: str,
        directory: Path,
        dark_mode: bool,
    ) -> str:
        """Process an include line."""
        # Handle !includeurl - pass through to server
        if re.match(r"^!includeurl\s+\S+\s*$", line):
            return temp_file + line

        # Handle !includesub
        if re.match(r"^!includesub\s+\S+\s*$", line):
            parts = line[11:].strip().split("!")
            if len(parts) == 2:
                inc_file = parts[0]
                sub_name = parts[1]

                if dark_mode:
                    inc_file = inc_file.replace(
                        self.config["theme_light"], self.config["theme_dark"]
                    )

                inc_path = self._resolve_include_path(diagram, directory, inc_file)
                if inc_path:
                    return self._read_include_sub(
                        diagram, temp_file, dark_mode, inc_path, sub_name
                    )
            raise Exception(f"Invalid !includesub syntax: {line}")

        # Handle !include
        if re.match(r"^!include\s+\S+\s*$", line):
            inc_file = line[9:].rstrip()

            if dark_mode:
                inc_file = inc_file.replace(
                    self.config["theme_light"], self.config["theme_dark"]
                )

            # Pass through URLs and stdlib includes
            if inc_file.startswith("http") or inc_file.startswith("<"):
                return temp_file + line

            inc_path = self._resolve_include_path(diagram, directory, inc_file)
            if inc_path:
                return self._read_include_file(diagram, temp_file, dark_mode, inc_path)

            raise Exception(f"Include could not be resolved: {line}")

        raise Exception(f"Unknown include type: {line}")

    def _resolve_include_path(
        self, diagram: Diagram, directory: Path, inc_file: str
    ) -> Optional[Path]:
        """Resolve include file path."""
        # Try relative to current directory
        inc_path = (directory / inc_file).resolve()
        if inc_path.exists():
            return inc_path

        # Try relative to root directory
        inc_path = (diagram.root_dir / inc_file).resolve()
        if inc_path.exists():
            return inc_path

        return None

    def _read_include_file(
        self,
        diagram: Diagram,
        temp_file: str,
        dark_mode: bool,
        inc_path: Path,
    ) -> str:
        """Read an included file and update mtime tracking."""
        try:
            inc_time = inc_path.stat().st_mtime
            if inc_time > diagram.inc_time:
                diagram.inc_time = inc_time
        except Exception:
            pass

        with inc_path.open("rt", encoding="utf-8") as f:
            included_content = self._read_file_recursive(
                f.readlines(),
                diagram,
                inc_path.parent,
                dark_mode,
            )
            # Append included content to temp_file, don't replace it
            return temp_file + included_content

    def _read_include_sub(
        self,
        diagram: Diagram,
        temp_file: str,
        dark_mode: bool,
        inc_path: Path,
        sub_name: str,
    ) -> str:
        """Read a sub from an included file."""
        # Update mtime tracking
        try:
            inc_time = inc_path.stat().st_mtime
            if inc_time > diagram.inc_time:
                diagram.inc_time = inc_time
        except Exception:
            pass

        with inc_path.open("rt", encoding="utf-8") as f:
            lines = f.readlines()
            in_sub = False
            sub_lines = []

            for line in lines:
                stripped = line.strip()
                # Match !startsub <sub_name>
                if re.match(rf"^!startsub\s+{re.escape(sub_name)}\s*$", stripped):
                    in_sub = True
                    continue
                # Match !endsub or @enduml (end of file)
                if re.match(r"^!endsub\s*$", stripped) or re.match(
                    r"^@enduml\s*$", stripped
                ):
                    in_sub = False
                    break
                if in_sub:
                    sub_lines.append(line)

            # Recursively process the sub content and append to temp_file
            sub_content = self._read_file_recursive(
                sub_lines,
                diagram,
                inc_path.parent,
                dark_mode,
            )
            return temp_file + sub_content

    def _encode_plantuml(self, content: str) -> str:
        """Encode PlantUML content to base64 format."""
        compressed = zlib.compress(content.encode("utf-8"))
        compressed_string = compressed[2:-4]  # Remove zlib header and checksum
        b64encoded = (
            base64.b64encode(compressed_string)
            .translate(b64_to_plantuml)
            .decode("utf-8")
        )
        return b64encoded

    async def _render_all_async(self, diagrams: List[Diagram]):
        """Render all diagrams in parallel using async HTTP."""
        semaphore = asyncio.Semaphore(self.config["max_concurrent_requests"])

        async with httpx.AsyncClient(
            verify=not self.config["disable_ssl_certificate_validation"],
            timeout=30.0,
        ) as client:
            tasks = []
            for diagram in diagrams:
                # Check if rendering is needed
                if self._needs_rendering(diagram, dark_mode=False):
                    tasks.append(
                        self._render_diagram_async(
                            client, semaphore, diagram, dark_mode=False
                        )
                    )
                if self.config["theme_enabled"] and self._needs_rendering(
                    diagram, dark_mode=True
                ):
                    tasks.append(
                        self._render_diagram_async(
                            client, semaphore, diagram, dark_mode=True
                        )
                    )

            await asyncio.gather(*tasks)

    def _needs_rendering(self, diagram: Diagram, dark_mode: bool) -> bool:
        """Check if diagram needs to be rendered."""
        out_file = diagram.out_file_dark if dark_mode else diagram.out_file
        out_path = diagram.out_dir / out_file

        try:
            img_time = out_path.stat().st_mtime
        except Exception:
            return True

        return (img_time < diagram.src_time) or (diagram.inc_time > img_time)

    async def _render_diagram_async(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        diagram: Diagram,
        dark_mode: bool,
    ):
        """Render a single diagram asynchronously."""
        async with semaphore:
            encoded = diagram.b64encoded_dark if dark_mode else diagram.b64encoded
            out_file = diagram.out_file_dark if dark_mode else diagram.out_file

            url = f"{self.config['server']}/{self.config['output_format']}/{encoded}"

            try:
                response = await client.get(url)
                if response.status_code == 200:
                    diagram.out_dir.mkdir(parents=True, exist_ok=True)
                    (diagram.out_dir / out_file).write_bytes(response.content)
                else:
                    print(
                        f"Error rendering {diagram.file}: HTTP {response.status_code}"
                    )
            except Exception as e:
                print(f"Error rendering {diagram.file}: {e}")
