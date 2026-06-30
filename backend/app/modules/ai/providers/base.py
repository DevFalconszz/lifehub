from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator


@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: str
    default_model: str
    models: list[str] = field(default_factory=list)


class AIProvider(ABC):
    config: ProviderConfig

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict:
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncGenerator[str, None]:
        ...

    def list_models(self) -> list[str]:
        return self.config.models
