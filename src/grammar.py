from symbol import Epsilon, Terminal, NonTerminal
from typing import List
from dataclasses import dataclass
from tokens import *


class Production:
    """Productions are rules that consist of a left-hand-side(LHS) and right-hand-side(RHS).
    The LHS is a single NonTerminal and the RHS is a list of Terminals and NonTerminals to replace the LHS
    when the production is applied.

    We can specify a production in the following maner.

    >>> Production(a, [b,c], nullable=True)
    >>> Production(a, [d,e], nullable=True)

    :param LHS: Left-hand-side of the production.
    :param RHS: Right-hand-side of the production.
    :param nullable: Specifies if the production is nullable.
    """

    number: int = 0

    def __init__(
        self,
        LHS: NonTerminal,
        RHS: List[NonTerminal | Terminal],
        nullable: bool = False,
        increment_number=True,
    ) -> None:
        self.LHS = LHS
        self.RHS = RHS
        self.nullable = nullable
        if increment_number:
            Production.number += 1
        self.number = Production.number

    def __str__(self) -> str:
        return f"{self.LHS}\t: {(' '.join([str(x) for x in self.RHS]))}\n"


class Grammar:
    def __init__(self) -> None:
        self.productions: List[Production] = []

    def append(self, prod: Production):
        self.productions.append(prod)

    def isNullable(self, nonterminal: NonTerminal) -> bool:
        for production in self.productions:
            if production.LHS == nonterminal:
                return production.nullable

        raise ValueError("Did not find Nonterninal as a LHS of any rule.")

    def terminals(self) -> List[Terminal]:
        """List all terminals which are subclasses of Token or Literal.
        Even terminals not in any RHS of any production in the grammar are listed.

        :return: All terminals.
        """
        terminals = []
        for production in self.productions:
            for symbol in production.RHS:
                if isinstance(symbol, Terminal):
                    terminals.append(symbol)
        return terminals
