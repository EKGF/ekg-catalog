"""
MkDocs hooks entry point.

This file is kept for backward compatibility with mkdocs.yml configuration.
It imports from the mkdocs package.
"""

import sys
from pathlib import Path

# Handle imports for both module and script execution
# When MkDocs loads this as a hook, it may not be in a package context,
# so we need to handle both absolute and relative imports
try:
    # Try relative import first (works when loaded as part of package)
    from .mkdocs.hooks import define_env, on_page_content, on_pre_build
except ImportError:
    # Fall back to absolute import (works when loaded directly by MkDocs or as script)
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from docs.mkdocs.hooks import define_env, on_page_content, on_pre_build

# Make hooks available at module level for MkDocs
__all__ = ["define_env", "on_page_content", "on_pre_build"]


# Entry point function for script execution
def main():
    """Entry point for running the generator as a script."""
    on_pre_build(None)


# When run as script, execute
if __name__ == "__main__":
    main()
