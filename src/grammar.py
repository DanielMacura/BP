from symbol import Epsilon, Terminal, NonTerminal
from typing import List, Set
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
        RHS: List[NonTerminal | Terminal] | Epsilon,
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
        return f"{self.LHS}\t-> {(' '.join([str(x) for x in self.RHS])) if not isinstance(self.RHS,Epsilon) else 'epsilon'}\n"


class Grammar:
    """The :py:class:`Grammar` is defined by a list of productions. It allows multiple operations, such as adding rules, checking if a :py:class:`NonTerminal` is nullable and returning all terminals.

    :param productions: List of productions defining a grammar.
    """

    def __init__(self) -> None:
        self.productions: List[Production] = []
        self.nullable_nonterminals: Set[NonTerminal] = set()

    def append(self, prod: Production):
        if prod.RHS == Epsilon():
            self.nullable_nonterminals |= {prod.LHS}
            prod.nullable = True
            for previous in self.productions:
                if previous.LHS == prod.LHS:
                    previous.nullable = True
        else:
            if prod.LHS in self.nullable_nonterminals:
                prod.nullable = True
        self.productions.append(prod)

    def isNullable(self, nonterminal: NonTerminal) -> bool:
        for production in self.productions:
            if production.LHS == nonterminal:
                return production.nullable

        raise ValueError("Did not find Nonterninal as a LHS of any rule.")

    def terminals(self) -> Set[Terminal]:
        """List all terminals which are subclasses of Token or Literal.
        Even terminals not in any RHS of any production in the grammar are listed.

        :return: All terminals.
        """
        terminals = set()
        for production in self.productions:
            if isinstance(production.RHS, Epsilon):
                continue
            for symbol in production.RHS:
                if isinstance(symbol, Terminal):
                    terminals.add(symbol)
        return terminals

    def nonTerminals(self) -> Set[NonTerminal]:
        """List all terminals which are subclasses of Token or Literal.
        Even terminals not in any RHS of any production in the grammar are listed.

        :return: All terminals.
        """
        nonTerminals = set()
        for production in self.productions:
            nonTerminals.add(production.LHS)
            if isinstance(production.RHS, Epsilon):
                continue
            for symbol in production.RHS:
                if isinstance(symbol, NonTerminal):
                    nonTerminals.add(symbol)
        return nonTerminals

    def __repr__(self) -> str:
        string = ""
        for production in self.productions:
            string += str(production.number) + str(production)
        return string
