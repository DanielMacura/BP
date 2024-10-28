from copyreg import constructor
from grammar import Grammar, Production
from symbol import Epsilon, NonTerminal, Terminal
from copy import deepcopy
import pprint
import pytest

from tokens import Token


class LLTable:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.firstSets = {}
        self.followSets = {}
        self.selectSets = {}

    def ComputeFirstSets(self):
        """Generate first sets for all the :py:class:`NonTerminal`s.
        Calls :py:meth:`FirstClosure` for every production.
        """
        self.firstSets = {prod.LHS: set() for prod in self.grammar.productions}
        # firstSets[NonTerminal("identifier")] = set()
        # firstSets[NonTerminal("expression")] = set()

        previousFirstSets = deepcopy(self.firstSets)
        while True:
            for production in self.grammar.productions:
                self.FirstClosure(production)
            if previousFirstSets == self.firstSets:
                break
            previousFirstSets = deepcopy(self.firstSets)

        for v, k in self.firstSets.items():
            print(v, k)


    def FirstClosure(self, production:Production)->None:
        """The first set for the production is found by applying one of the follwing rules to a production in the form of

        lhs -> a b c; where **lhs** is a single nonterminal, **a** is zero or more nullable nonterminals, **b** is a single terminal or non-nullable nonterminal and **c** is a series of terminals and nonterminals.

        1. If **a** preceeding **b** is empty, FIRST(lhs) = **b**
        2. Otherwise FIRST(lhs) = {each nonterminal from **a**} and **b**

        This closure needs to be applied to all productions in the grammar, until they don't change after aplication.

        :param production: Production who's first set will be computed and added to :py:attribute:`firstSets`.
        """
        for symbol in production.RHS:
            if isinstance(symbol, Terminal):
                self.firstSets[production.LHS] |= {symbol}
                return
            else:
                self.firstSets[production.LHS] |= self.firstSets[symbol]
                if not self.grammar.isNullable(symbol):
                    return

    def ComputeFolowSets(self):
        """Generate follow sets for all the :py:class:`NonTerminal`s. Called after :py:meth:`ComputeFirstSets`.
        Calls :py:meth:`FirstClosure` for every production.
        """
        self.followSets = {prod.LHS: set() for prod in self.grammar.productions}
        previousFollowSets = deepcopy(self.followSets)

        while True:
            for production in self.grammar.productions:
                self.FollowClosure(production)
            if previousFollowSets == self.followSets:
                break
            previousFollowSets = deepcopy(self.followSets)

    def FollowClosure(self, production:Production) -> None:
        """The follow set for the production is found with the following steps for any production in the form of

        lhs -> a b c; where **lhs** is a single nonterminal, **a** is zero or more nullable nonterminals, **b** is a single terminal or non-nullable nonterminal and **c** is a series of terminals and nonterminals.

        1. If **a** preceeding **b** is empty, FIRST(lhs) = **b**
        2. Otherwise FIRST(lhs) = {each nonterminal from **a**} and **b**

        This closure needs to be applied to all productions in the grammar, until they don't change after aplication.

        :param production: Production who's first set will be computed and added to :py:attribute:`firstSets`.
        """
        foundNonterminal: None | NonTerminal = None
        # First rule application
        for symbol in production.RHS:
            if isinstance(symbol, NonTerminal):
                if self.grammar.isNullable(symbol):
                    if foundNonterminal:
                        self.followSets[foundNonterminal] |= self.firstSets[symbol]
                else:
                    if foundNonterminal:
                        self.followSets[foundNonterminal] |= self.firstSets[symbol]
                foundNonterminal = symbol

            elif isinstance(symbol, Terminal) or isinstance(symbol, Epsilon):
                if foundNonterminal:
                    self.followSets[foundNonterminal] |= {symbol}

        # Second rule application
        for symbol in reversed(production.RHS):
            if isinstance(symbol, NonTerminal):
                self.followSets[symbol] |= self.followSets[production.LHS]
                if not self.grammar.isNullable((symbol)):
                    return
            elif isinstance(symbol, Terminal):
                return

    def ComputeSelectSets(self):
        selectSets = {prod.number: set() for prod in self.grammar.productions}
        for production in self.grammar.productions:
            for symbol in production.RHS:
                if production.nullable:
                    if isinstance(symbol, NonTerminal):
                        selectSets[production.number] |= self.firstSets[symbol]
                    selectSets[production.number] |= self.followSets[production.LHS]
                
                if isinstance(symbol, NonTerminal):
                    selectSets[production.number] |= self.firstSets[symbol]
                    if not self.grammar.isNullable(symbol):
                        break
                else:
                    selectSets[production.number] |= {symbol}
                    break
        for k, v in selectSets.items():
            print(k, v)
        self.selectSets = selectSets


    def Predict(self, currentState:NonTerminal, token:Token) -> Production|None:
        """Used to guide the parsing process. When in the state :py:attribute:`currentState`, depending on the current input token, the next valid production is returned.
        If an invalid token for the current state is parsed, None is returned.

        :param currentState: 
        :param token: 
        :return: 
        """
        
        return self.table[currentState][token] 

    def ComputeTable(self):
        print("Selectt\n", self.selectSets)
        table = {prod.LHS: {token: None for token in self.grammar.terminals()} for prod in self.grammar.productions}
        for production in self.grammar.productions:
            for token in self.selectSets[production.number]:
                table[production.LHS][token] = production
        print(table)
        for production in self.grammar.productions:
            for token in self.grammar.terminals():
                print(table[production.LHS][token], end='')
            print()
        self.table = table
        pp = pprint.PrettyPrinter(depth=2)
        pp.pprint(table)
