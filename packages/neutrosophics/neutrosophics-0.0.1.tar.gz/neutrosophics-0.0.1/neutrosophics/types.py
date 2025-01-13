from typing import Union, Tuple
from dataclasses import dataclass
from .validators import Validatable


@dataclass
class NetrosophicSet(Validatable):
    truth: float
    indeterminacy: float
    falsity: float

    def __new__(cls, truth: float, indeterminacy: float, falsity: float):
        instance = super().__new__(cls)
        instance.truth = truth
        instance.indeterminacy = indeterminacy
        instance.falsity = falsity
        return instance

    def __post_init__(self):
        self.validate()

    def validate(self):
        for value in (self.truth, self.indeterminacy, self.falsity):
            if not (0.0 <= value <= 1.0):
                raise ValueError("Netrosophic set values must be in the range [0, 1]")

    def __add__(self, other: 'NetrosophicSet') -> 'NetrosophicSet':
        return NetrosophicSet(
            min(self.truth + other.truth, 1.0),
            min(self.indeterminacy + other.indeterminacy, 1.0),
            min(self.falsity + other.falsity, 1.0)
        )

    def __sub__(self, other: 'NetrosophicSet') -> 'NetrosophicSet':
        return NetrosophicSet(
            max(self.truth - other.truth, 0.0),
            max(self.indeterminacy - other.indeterminacy, 0.0),
            max(self.falsity - other.falsity, 0.0)
        )

    def __mul__(self, other: Union['NetrosophicSet', float]) -> 'NetrosophicSet':
        if isinstance(other, NetrosophicSet):
            return NetrosophicSet(
                self.truth * other.truth,
                self.indeterminacy * other.indeterminacy,
                self.falsity * other.falsity
            )
        elif isinstance(other, (int, float)):
            return NetrosophicSet(
                min(self.truth * other, 1.0),
                min(self.indeterminacy * other, 1.0),
                min(self.falsity * other, 1.0)
            )
        else:
            raise TypeError("Unsupported operand type for multiplication")

    def __truediv__(self, other: float) -> 'NetrosophicSet':
        if other == 0:
            raise ZeroDivisionError("Division by zero")
        return NetrosophicSet(
            min(self.truth / other, 1.0),
            min(self.indeterminacy / other, 1.0),
            min(self.falsity / other, 1.0)
        )

    @classmethod
    def from_tuple(cls, values: Tuple[float, float, float]) -> 'NetrosophicSet':
        return cls(*values)

    def to_tuple(self) -> Tuple[float, float, float]:
        return self.truth, self.indeterminacy, self.falsity
