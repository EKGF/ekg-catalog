"""MkDocs plugins and hooks."""

from .hooks import on_env, on_page_content, on_pre_build

__all__ = ["on_env", "on_page_content", "on_pre_build"]
