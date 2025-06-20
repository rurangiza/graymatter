from abc import ABC, abstractmethod

from pydantic import BaseModel


class Tool(BaseModel, ABC):
    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @classmethod
    def description(cls) -> str | None:
        return cls.__doc__

    @abstractmethod
    async def resolve(self) -> str:
        pass
