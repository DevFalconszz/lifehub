from __future__ import annotations

import json
from typing import Any, AsyncGenerator

from app.modules.ai.providers.registry import ProviderRegistry
from app.modules.ai.tools.registry import ToolRegistry
from app.modules.ai.tools.tool_factory import build_tool_registry

SYSTEM_PROMPT = """You are LifeHub AI, a personal assistant integrated into the user's LifeHub system.

You have access to tools that let you interact with the user's data:
- Projects and Tasks (todo management)
- Notes (markdown notes)
- Finances (transactions and budgets)
- Calendar (events)
- Readings (bookmarks and reading list)

## How to use tools
1. Call `learn_tools` with the tool names you need to discover their input schemas.
2. Once you know the schema, call `execute_tool` with the tool name and proper arguments.
3. Interpret the results and present them to the user in a helpful way.

Always be concise and helpful. Use markdown formatting when appropriate.
The current date is 2026-06-29."""


def _get_provider(provider_registry, provider_key):
    if provider_registry:
        provider = provider_registry.get(provider_key)
        if provider:
            return provider
    from app.modules.ai.providers.registry import get_provider_registry
    return get_provider_registry().get(provider_key)


def _meta_tools(tool_registry: ToolRegistry) -> list[dict]:
    return [
        tool_registry.get_learn_tools_schema(),
        tool_registry.get_execute_tool_schema(),
    ]


class ChatService:
    def __init__(
        self,
        user: dict,
        provider_registry: ProviderRegistry | None = None,
    ):
        self.user = user
        self.provider_registry = provider_registry
        self.tool_registry = build_tool_registry(user['id'])

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        provider_key: str = 'openzen',
    ) -> dict:
        provider = _get_provider(self.provider_registry, provider_key)
        full_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + messages
        return await self._chat_with_tools(full_messages, provider, model)

    async def chat_stream(
        self,
        messages: list[dict],
        model: str | None = None,
        provider_key: str = 'openzen',
    ) -> AsyncGenerator[str, None]:
        provider = _get_provider(self.provider_registry, provider_key)
        full_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + messages

        resolved = await self._resolve_tool_calls(full_messages, provider, model)
        content = resolved['choices'][0]['message'].get('content', '')

        if content:
            for i in range(0, len(content), 50):
                chunk = content[i:i + 50]
                sse = json.dumps({
                    'id': resolved.get('id', ''),
                    'object': 'chat.completion.chunk',
                    'choices': [{'index': 0, 'delta': {'content': chunk}, 'finish_reason': None}],
                })
                yield f'data: {sse}\n\n'

        done = json.dumps({
            'id': resolved.get('id', ''),
            'object': 'chat.completion.chunk',
            'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}],
        })
        yield f'data: {done}\n\n'
        yield 'data: [DONE]\n\n'

    async def _resolve_tool_calls(
        self,
        messages: list[dict],
        provider,
        model: str | None,
        max_depth: int = 10,
    ) -> dict:
        for _ in range(max_depth):
            response = await provider.chat(
                messages=messages,
                model=model,
                tools=_meta_tools(self.tool_registry),
                tool_choice='auto',
            )

            choice = response['choices'][0]
            message = choice['message']

            if not message.get('tool_calls'):
                return response

            messages = await self._apply_tool_calls(message['tool_calls'], messages, provider, model)

        raise RuntimeError('Tool call recursion exceeded max depth')

    async def _apply_tool_calls(
        self,
        tool_calls: list[dict],
        messages: list[dict],
        provider,
        model: str | None,
    ) -> list[dict]:
        tool_results = []
        for tc in tool_calls:
            func_name = tc['function']['name']
            try:
                args = json.loads(tc['function']['arguments'])
            except json.JSONDecodeError:
                args = {}

            if func_name == 'learn_tools':
                names = args.get('tool_names', [])
                infos = self.tool_registry.get_tool_info(names)
                result = json.dumps([{
                    'name': ti.name,
                    'description': ti.description,
                    'input_schema': ti.input_schema,
                    'category': ti.category,
                } for ti in infos], indent=2)

            elif func_name == 'execute_tool':
                tool_name = args.get('name', '')
                tool_args = args.get('arguments', {})
                try:
                    output = await self.tool_registry.execute_tool(tool_name, tool_args)
                    result = json.dumps({'success': True, 'data': str(output)}, indent=2, default=str)
                except Exception as e:
                    result = json.dumps({'success': False, 'error': str(e)}, indent=2)

            else:
                result = json.dumps({'error': f'Unknown tool: {func_name}'})

            tool_results.append({
                'role': 'tool',
                'tool_call_id': tc['id'],
                'content': result,
            })

        messages.append({
            'role': 'assistant',
            'content': None,
            'tool_calls': tool_calls,
        })
        messages.extend(tool_results)
        return messages

    async def _chat_with_tools(
        self,
        messages: list[dict],
        provider,
        model: str | None,
    ) -> dict:
        return await self._resolve_tool_calls(messages, provider, model)
