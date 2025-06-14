from openai import pydantic_function_tool

from graymatter.tools import Tool, ToolRegistry
from graymatter.tools.constants import ModelProvider
from graymatter.tools.exceptions import ToolNotFound, UnsupportedProvider

from .implementations import GetDate


class BaseRegistry(ToolRegistry):
    _tool_classes = list[type[Tool]] = [GetDate]

    def __init__(self) -> None:
        self._tools = {tool.name(): tool for tool in BaseRegistry._tool_classes}

    @property
    def tools(self) -> dict[str, type[Tool]]:
        return self._tools

    @property
    def tool_definitions(
        self, provider: ModelProvider = ModelProvider.OPENAI
    ) -> list[dict]:
        match provider:
            case ModelProvider.OPENAI:
                return [pydantic_function_tool(tool) for tool in self.tools()]
            case _:
                raise UnsupportedProvider()

    def get_tool_by_name(self, tool_name: str) -> type[Tool]:
        if tool_name not in self._tools:
            raise ToolNotFound()
        return self._tools[tool_name]

    def get_tool_definition_by_name(
        self, tool_name: str, provider: ModelProvider = ModelProvider.OPENAI
    ) -> dict:
        match provider:
            case ModelProvider.OPENAI:
                tool = self.get_tool_by_name(tool_name)
                return pydantic_function_tool(tool)
            case _:
                raise UnsupportedProvider()
