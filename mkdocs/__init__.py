"""MkDocs plugins and hooks."""

# Make the async plugin available
from .plantuml_async import AsyncPlantUMLPlugin

__all__ = ["AsyncPlantUMLPlugin"]
