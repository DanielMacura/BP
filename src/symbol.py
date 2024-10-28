from dataclasses import dataclass


@dataclass
class Symbol:
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

class Terminal(Symbol):

    def __str__(self) -> str:
        return self.__class__.__name__
    def __hash__(self):
        return super().__hash__()
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


@dataclass
class NonTerminal(Symbol):
    name: str

    def __str__(self) -> str:
        return self.name
    def __hash__(self):
        return super().__hash__()
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

class Epsilon(Symbol):
    def __str__(self) -> str:
        return "Epsilon"
    def __hash__(self):
        return super().__hash__()
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
