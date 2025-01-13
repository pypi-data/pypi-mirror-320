from __future__ import annotations
from abc import ABC, abstractmethod
from .types import NetrosophicSet

# Interface for logical operations
class LogicalOperations(ABC):
    @abstractmethod
    def conjunction(self, other: 'NetrosophicSet') -> 'NetrosophicSet':
        pass

    @abstractmethod
    def disjunction(self, other: 'NetrosophicSet') -> 'NetrosophicSet':
        pass

    @abstractmethod
    def negation(self) -> 'NetrosophicSet':
        pass


class NetrosophicLogic(LogicalOperations):
    def conjunction(self, ns1: NetrosophicSet, ns2: NetrosophicSet) -> NetrosophicSet:
        return NetrosophicSet(
            min(ns1.truth, ns2.truth),
            max(ns1.indeterminacy, ns2.indeterminacy),
            max(ns1.falsity, ns2.falsity)
        )

    def disjunction(self, ns1: NetrosophicSet, ns2: NetrosophicSet) -> NetrosophicSet:
        return NetrosophicSet(
            max(ns1.truth, ns2.truth),
            min(ns1.indeterminacy, ns2.indeterminacy),
            min(ns1.falsity, ns2.falsity)
        )

    def negation(self, ns: NetrosophicSet) -> NetrosophicSet:
        return NetrosophicSet(
            1.0 - ns.truth,
            ns.indeterminacy,
            1.0 - ns.falsity
        )
