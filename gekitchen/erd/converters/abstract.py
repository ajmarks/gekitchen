from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class ErdValueConverter(Generic[T], ABC):
    @abstractmethod
    def erd_encode(self, value: T) -> str:
        pass
    @abstractmethod
    def erd_decode(self, value: str) -> T:
        pass

class ErdReadOnlyConverter(ErdValueConverter[T]):
    def erd_encode(self, value: T) -> str:
        raise NotImplementedError



