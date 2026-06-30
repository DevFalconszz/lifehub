from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from app.modules.ai.providers.base import AIProvider, ProviderConfig


class OpenCodeZenProvider(AIProvider):
    def __init__(self, config: ProviderConfig | None = None):
        self.config = config or ProviderConfig(
            name='openzen',
            api_key='public',
            base_url='https://opencode.ai/zen/v1',
            default_model='deepseek-v4-flash-free',
            models=['deepseek-v4-flash-free'],
        )

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict:
        payload = self._build_payload(messages, model, tools, tool_choice, max_tokens, temperature)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.config.base_url}/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.config.api_key}',
                },
                json=payload,
                timeout=120,
            )
            if response.status_code == 429:
                raise RuntimeError(f'Rate limit exceeded: {response.text}')
            if not response.is_success:
                raise RuntimeError(f'Provider error {response.status_code}: {response.text}')
            return response.json()

    async def chat_stream(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncGenerator[str, None]:
        payload = self._build_payload(messages, model, tools, tool_choice, max_tokens, temperature)
        payload['stream'] = True

        async with httpx.AsyncClient() as client:
            async with client.stream(
                'POST',
                f'{self.config.base_url}/chat/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.config.api_key}',
                },
                json=payload,
                timeout=120,
            ) as response:
                if not response.is_success:
                    error_text = await response.aread()
                    raise RuntimeError(f'Provider error {response.status_code}: {error_text.decode()}')

                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]
                        if data.strip() == '[DONE]':
                            break
                        yield data

    def _build_payload(
        self,
        messages: list[dict],
        model: str | None,
        tools: list[dict] | None,
        tool_choice: str | dict | None,
        max_tokens: int | None,
        temperature: float | None,
    ) -> dict:
        payload: dict = {
            'model': model or self.config.default_model,
            'messages': messages,
        }
        if tools:
            payload['tools'] = tools
        if tool_choice:
            payload['tool_choice'] = tool_choice
        if max_tokens:
            payload['max_tokens'] = max_tokens
        if temperature is not None:
            payload['temperature'] = temperature
        return payload
