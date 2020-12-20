from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class ErdValueConverter(Generic[T], ABC):
    @staticmethod
    @abstractmethod
    def erd_encode(value: T) -> str:
        pass
    @staticmethod
    @abstractmethod
    def erd_decode(value: str) -> T:
        pass

class ErdReadOnlyConverter(ErdValueConverter[T]):
    @staticmethod
    def erd_encode(value: T) -> str:
        raise NotImplementedError



