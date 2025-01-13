from __future__ import annotations
from abc import ABC, abstractmethod
from .types import NetrosophicSet


# Interface for analysis
class Analyzable(ABC):
    @abstractmethod
    def analyze(self) -> str:
        pass


class NetrosophicAnalyzer(Analyzable):
    def analyze(self, ns: NetrosophicSet) -> str:
        return (
            f"Analysis:\n"
            f"  Truth Degree: {ns.truth}\n"
            f"  Indeterminacy Degree: {ns.indeterminacy}\n"
            f"  Falsity Degree: {ns.falsity}\n"
            f"  Overall Certainty: {ns.truth - ns.falsity}"
        )
