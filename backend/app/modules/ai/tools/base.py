from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema
    execute: Callable[..., Any]
    category: str = 'general'


@dataclass
class ToolInfo:
    name: str
    description: str
    input_schema: dict
    category: str
