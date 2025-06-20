class ToolNotFound(Exception):
    def __init__(self) -> None:
        self.message = "Tool Not Found"
        super().__init__(self.message)


class ToolAlreadyExists(Exception):
    def __init__(self) -> None:
        self.message = "Tool Already Exists"
        super().__init__(self.message)


class UnsupportedProvider(Exception):
    def __init__(self) -> None:
        self.message = "Unsupported Provider"
        super().__init__(self.message)


class ToolError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class NoSearchResultFound(Exception):
    def __init__(self, query) -> None:
        self.message = f"No search results found for query: {query}"
        super().__init__(self.message)
