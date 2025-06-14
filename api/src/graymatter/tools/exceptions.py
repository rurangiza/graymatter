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
