from __future__ import annotations

from app.modules.ai.providers.base import AIProvider, ProviderConfig
from app.modules.ai.providers.openzen import OpenCodeZenProvider


class ProviderRegistry:
    providers: dict[str, AIProvider]

    def __init__(self):
        self.providers = {}

    def register(self, key: str, provider: AIProvider) -> None:
        self.providers[key] = provider

    def get(self, key: str) -> AIProvider:
        provider = self.providers.get(key)
        if not provider:
            raise ValueError(f'Unknown provider: {key}. Available: {list(self.providers.keys())}')
        return provider

    def resolve_model(self, model_id: str) -> tuple[AIProvider, str]:
        if '/' in model_id:
            provider_key, model_name = model_id.split('/', 1)
            provider = self.get(provider_key)
            return provider, model_name
        provider_key = 'openzen'
        model_name = model_id
        return self.get(provider_key), model_name

    def list_available(self) -> list[dict]:
        return [
            {'key': key, 'name': p.config.name, 'models': p.list_models()}
            for key, p in self.providers.items()
        ]

    def configure_openzen(
        self,
        api_key: str = 'public',
        base_url: str = 'https://opencode.ai/zen/v1',
        default_model: str = 'deepseek-v4-flash-free',
    ) -> OpenCodeZenProvider:
        provider = OpenCodeZenProvider(ProviderConfig(
            name='OpenCode Zen',
            api_key=api_key,
            base_url=base_url,
            default_model=default_model,
            models=[default_model],
        ))
        self.register('openzen', provider)
        return provider


_default_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = ProviderRegistry()
        _default_registry.configure_openzen()
    return _default_registry
