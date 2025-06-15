from abc import ABC
from enum import StrEnum

from .tool import Tool


class ModelProvider(StrEnum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


class ToolRegistry(ABC):
    @property
    def tools(self) -> dict[str, type[Tool]]:
        pass

    @property
    def tool_definitions(
        self, provider: ModelProvider = ModelProvider.OPENAI
    ) -> list[dict]:
        pass

    def get_tool_by_name(self, tool_name: str) -> type[Tool]:
        pass

    def get_tool_definitions_by_names(
        self, tool_names: list[str], provider: ModelProvider = ModelProvider.OPENAI
    ) -> dict | None:
        pass
