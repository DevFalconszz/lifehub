from __future__ import annotations

import json
from typing import Any

from app.modules.ai.tools.base import Tool, ToolInfo


class ToolRegistry:
    tools: dict[str, Tool]

    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool | None:
        return self.tools.get(name)

    def get_tool_info(self, names: list[str]) -> list[ToolInfo]:
        result = []
        for name in names:
            tool = self.get_tool(name)
            if tool:
                result.append(ToolInfo(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.parameters,
                    category=tool.category,
                ))
        return result

    async def execute_tool(self, name: str, args: dict) -> Any:
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f'Unknown tool: {name}')
        result = tool.execute(**args)
        if hasattr(result, '__await__'):
            result = await result
        return result

    def build_catalog_text(self) -> str:
        lines = ['## Available Tools\n']
        for name, tool in sorted(self.tools.items()):
            lines.append(f'- **{name}** ({tool.category}): {tool.description}')
            lines.append(f'  Parameters: {json.dumps(tool.parameters, indent=2)}')
        return '\n'.join(lines)

    def build_openai_tools(self) -> list[dict]:
        return [
            {
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.parameters,
                },
            }
            for tool in self.tools.values()
        ]

    def get_learn_tools_schema(self) -> dict:
        return {
            'type': 'function',
            'function': {
                'name': 'learn_tools',
                'description': 'Learn the input schemas for tools you want to use. Call this first to discover parameters.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'tool_names': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'Names of tools to learn about',
                        },
                    },
                    'required': ['tool_names'],
                },
            },
        }

    def get_execute_tool_schema(self) -> dict:
        return {
            'type': 'function',
            'function': {
                'name': 'execute_tool',
                'description': 'Execute a tool with the given arguments. Use learn_tools first to get the schema.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Tool name to execute'},
                        'arguments': {'type': 'object', 'description': 'Arguments for the tool (must match the tool\'s JSON Schema)'},
                    },
                    'required': ['name', 'arguments'],
                },
            },
        }
