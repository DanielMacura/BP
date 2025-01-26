from grammar import Grammar, Production
from symbol import Epsilon, NonTerminal, Terminal
from copy import deepcopy
import pprint

from tokens import Token


class LLTable:
    def __init__(self, grammar: Grammar) -> None:
        """LLTable constructor.

        :param grammar: LL(1) grammar.
        """
        self.grammar = grammar
        self.firstSets = {}
        self.followSets = {}
        self.selectSets = {}

    def ComputeFirstSets(self):
        """Generate first sets for all the :py:class:`NonTerminal` s.
        Calls :py:meth:`FirstClosure` for every production.
        """
        self.firstSets = {prod.LHS: set() for prod in self.grammar.productions}

        previousFirstSets = deepcopy(self.firstSets)
        while True:
            for production in self.grammar.productions:
                self.FirstClosure(production)
            if previousFirstSets == self.firstSets:
                break
            previousFirstSets = deepcopy(self.firstSets)

        for v, k in self.firstSets.items():
            print(v, k)

    def FirstClosure(self, production: Production) -> None:
        """The first set for the production is found by applying the follwing rule to a production in the form of

        .. math::
            lhs \\rightarrow \\alpha \\beta \\mathcal{B}

        where :math:`lhs` is a single nonterminal, :math:`\\alpha` is zero or more **nullable** nonterminals, :math:`\\beta` is a single terminal or non-nullable nonterminal and :math:`\\mathcal{B}` is a series of terminals and nonterminals.


        1. FIRST(A), where A is a terminal is {A}.
        2. FIRST(:math:`lhs`) = FIRST(:math:`\\alpha`) and FIRST(:math:`\\beta`)


        This closure needs to be applied to all productions in the grammar, until they don't change after aplication.

        :param production: Production who's first set will be computed and added to :py:attr:`firstSets`.
        """
        if type(production.RHS) is Epsilon:
            return
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

    def FollowClosure(self, production: Production) -> None:
        """The follow set for the production is found with the following steps for any production in the form of

        .. math::
            lhs \\rightarrow \\dots a \\alpha \\beta \\dots

        where :math:`lhs` is a single nonterminal, :math:`a` is single  **non**-nullable nonterminal, :math:`\\alpha` is a series of 0 or more nullable nonterminals and :math:`\\beta` is a single terminal or **non**-nullable nonterminal.

        FOLLOW(:math:`a`) includes FIRST(:math:`\\alpha`) and FIRST(:math:`\\beta`)

        .. math::
            lhs \\rightarrow \\dots a \\alpha

        where :math:`lhs` and :math:`a` are nonterminals, :math:`a` may be nullable, and :math:`\\alpha` is a series of zero or more nullable nonterminals. FOLLOW(:math:`lhs`) is added to FOLLOW(:math:`a`).

        This closure needs to be applied to all productions in the grammar, until they don't change after aplication.

        :param production: Production who's first set will be computed and added to :py:attr:`firstSets`.
        """
        if isinstance(production.RHS, Epsilon):
            print("Epsion prod", production)
            return
        # First rule application
        for i, symbol in enumerate(production.RHS[:-1]):
            if isinstance(symbol, NonTerminal):
                next_symbol = production.RHS[i + 1]
                if isinstance(next_symbol, Terminal):
                    self.followSets[symbol] |= {next_symbol}
                elif isinstance(next_symbol, NonTerminal):
                    self.followSets[symbol] |= self.firstSets[next_symbol]
            if isinstance(symbol, Terminal):
                continue
        # Second rule application
        last_nonterminal: None | NonTerminal = None
        print("Rule", production.LHS, production.RHS, self.followSets[production.LHS])
        for symbol in reversed(production.RHS):
            if isinstance(symbol, NonTerminal):
                last_nonterminal = symbol

                self.followSets[symbol] |= self.followSets[production.LHS]
                if not self.grammar.isNullable((symbol)):
                    break
            elif isinstance(symbol, Terminal):
                break
        if last_nonterminal is not None:
            print("---ADDING", self.followSets[production.LHS], "to", last_nonterminal)
            self.followSets[last_nonterminal] |= self.followSets[production.LHS]

    def ComputeSelectSets(self):
        """Generate select sets for all the :py:class:`NonTerminal`s. Called after :py:meth:`ComputeFollowSets`.

        If a production is nullable, it's whole RHS can go to epsilon, then given a production of the form

        .. math::
            lhs \\rightarrow \\alpha

        where :math:`\\alpha` is series of zero or more nullable nonterminals, SELECT(:math:`lhs`) is FIRST(:math:`\\alpha`) and FOLLOW(:math:`lhs`)

        If a production is not nullable, then given

        .. math::
            lhs \\rightarrow \\alpha \\beta \\dots

        where :math:`\\alpha` is series of zero or more nullable nonterminals and :math:`\\beta` is either **non**-nullable nonterninal or a terminal, then LL(:math:`lhs`) is FIRST(:math:`\\alpha`) and FIRST(:math:`\\beta`).
        """
        selectSets = {prod.number: set() for prod in self.grammar.productions}
        for production in self.grammar.productions:
            if isinstance(production.RHS, Epsilon):
                selectSets[production.number] |= self.followSets[production.LHS]
                continue
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
        print("Select sets")
        for k, v in selectSets.items():
            print(k, v)
        self.selectSets = selectSets

    def Predict(self, currentState: NonTerminal, token: Token) -> Production | None:
        """Used to guide the parsing process. When in the state :py:attr:`currentState`, depending on the current input token, the next valid production is returned.
        If an invalid token for the current state is parsed, None is returned.

        :param currentState: The current :py:class:`NonTerminal` on the top of the :py:class:`Parser` stack.
        :param token: The current input :py:class:`Token`.
        :return: Return a valid :py:class:`Token` or None.
        """

        return self.table[currentState][token]

    def ComputeTable(self):
        """
        Computes the LL table from the SELECT sets for each terminal and nonterminal.

        :py:meth:`ComputeFirstSets`, :py:meth:`ComputeFollowSets` and :py:meth:`ComputeSelectSets` are called first.
        """
        self.ComputeFirstSets()
        self.ComputeFolowSets()
        self.ComputeSelectSets()
        print("Selectt\n", self.selectSets)
        table = {
            prod.LHS: {token: None for token in self.grammar.terminals()}
            for prod in self.grammar.productions
        }
        for production in self.grammar.productions:
            for token in self.selectSets[production.number]:
                table[production.LHS][token] = production
        self.table = table
        pp = pprint.PrettyPrinter(depth=2)
        pp.pprint(table)

    def __repr__(self) -> str:
        """Return a csv representation of the LL table.

        :return: csv string of LL table.
        """
        csv_string = ","
        header = ",".join(sorted([str(x) for x in self.grammar.terminals()]))
        csv_string += header + "\n"
        for row in sorted(
            [x for x in self.grammar.nonTerminals()], key=lambda x: str(x)
        ):
            csv_string += str(row) + ","
            for token in sorted(
                [x for x in self.grammar.terminals()], key=lambda x: str(x)
            ):
                csv_string += (
                    str(self.table[row][token].number)
                    if self.table[row][token] is not None
                    else " "
                ) + ","
            csv_string += "\n"
        return csv_string
