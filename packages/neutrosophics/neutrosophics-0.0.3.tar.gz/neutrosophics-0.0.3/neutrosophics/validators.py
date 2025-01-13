from abc import ABC, abstractmethod


# Interface for validation
class Validatable(ABC):
    @abstractmethod
    def validate(self):
        pass
