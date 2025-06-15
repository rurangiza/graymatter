from openai import pydantic_function_tool

from graymatter.tools.constants import ModelProvider
from graymatter.tools.exceptions import ToolNotFound, UnsupportedProvider

from ._abstract_registry import ToolRegistry
from .implementations import GetDate
from .tool import Tool


class BaseRegistry(ToolRegistry):
    _tool_classes: list[Tool] = [GetDate]

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

    def get_tool_definitions_by_names(
        self, tool_names: list[str], provider: ModelProvider = ModelProvider.OPENAI
    ) -> dict | None:
        match provider:
            case ModelProvider.OPENAI:
                tool_definitions = [
                    pydantic_function_tool(self.get_tool_by_name(tool_name))
                    for tool_name in tool_names
                ]
                if len(tool_definitions) != len(tool_names):
                    raise ToolNotFound("Found less tools than expected")
                if len(tool_definitions) == 0:
                    return None
                return tool_definitions
            case _:
                raise UnsupportedProvider("")
