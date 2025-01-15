from abc import ABC, abstractmethod
from eo4eu_base_utils.result import Result


class Source(ABC):
    @abstractmethod
    def get(self, args) -> Result:
        return Result.err("")


class Filler(ABC):
    @abstractmethod
    def fill(self, source: Source, val: Result) -> Result:
        return None
