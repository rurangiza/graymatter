from openai.types.chat import ChatCompletionMessageParam as CompletionMessage
from openai.types.chat import ChatCompletionMessageToolCall as ToolCallMessage


def execute_tools(
    messages: list[CompletionMessage], tool_calls: list[ToolCallMessage]
) -> list[CompletionMessage]:
    for tool_call in tool_calls:
        function_name = ...
        args = ...
