from openai.types import CompletionUsage


class Usage:
    def __init__(self):
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.total_tokens = 0

    def __iadd__(self, other: CompletionUsage):
        self.completion_tokens += other.completion_tokens
        self.prompt_tokens += other.prompt_tokens
        self.total_tokens += other.total_tokens
        return self

    def dict(self) -> dict:
        return {
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens,
        }

    def __repr__(self) -> str:
        return f"Completion Usage (prompt_tokens: {self.prompt_tokens}, completion_tokens: {self.completion_tokens}, total_tokens: {self.total_tokens})"
