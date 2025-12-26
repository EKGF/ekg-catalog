"""MkDocs plugins package."""

# Make hooks available at package level
from .hooks import define_env, on_page_content, on_pre_build

__all__ = ["define_env", "on_page_content", "on_pre_build"]
