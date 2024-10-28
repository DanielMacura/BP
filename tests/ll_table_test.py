from grammar import Grammar, Production
from symbol import NonTerminal
from tokens import Integer, LeftBracket, Multiply, Plus, RightBracket, Semicolon, Token
from lltable import LLTable
import pytest
from copy import deepcopy


@pytest.fixture
def test_grammar() -> Grammar:
    """
    #TODO Cite me - Alan Holub
    """
    stmt = NonTerminal("stmt")
    expr = NonTerminal("expr")
    expr_p = NonTerminal("expr_p")
    term = NonTerminal("term")
    term_p = NonTerminal("term_p")
    factor = NonTerminal("factor")

    test_grammar = deepcopy(Grammar())

    test_grammar.append(Production(stmt, [expr, Semicolon()]))
    test_grammar.append(Production(expr, [term, expr_p], nullable=True))
    test_grammar.append(Production(expr_p, [Plus(), term, expr_p], nullable=True))
    test_grammar.append(Production(term, [factor, term_p]))
    test_grammar.append(Production(term_p, [Multiply(), factor, term_p], nullable=True))
    test_grammar.append(Production(factor, [LeftBracket(), expr, RightBracket()]))
    test_grammar.append(Production(factor, [Integer()]))
    return deepcopy(test_grammar)


@pytest.fixture(autouse=True)
def test_grammar_simple() -> Grammar:
    """
    #TODO Cite me - Alan Holub
    """
    stmt = NonTerminal("stmt")
    dec_term = NonTerminal("dec_term")

    test_grammar_simple = Grammar()

    class Perkin_Elmer(Token):
        pass

    class ADM3(Token):
        pass

    class VT52(Token):
        pass

    class VT100(Token):
        pass

    test_grammar_simple.append(Production(stmt, [Perkin_Elmer()]))
    test_grammar_simple.append(Production(stmt, [ADM3()]))
    test_grammar_simple.append(Production(stmt, [dec_term]))
    test_grammar_simple.append(Production(dec_term, [VT52()]))
    test_grammar_simple.append(Production(dec_term, [VT100()]))
    return deepcopy(test_grammar_simple)


# def test_first_sets(test_grammar):
#     print("Test")
#
#     table = LLTable(test_grammar)
#     table.ComputeFirstSets()
#     assert False
#
# def test_follow_sets(test_grammar):
#
#
#     table = LLTable(test_grammar)
#
#     table.ComputeFirstSets()
#     table.ComputeFolowSets()
#
#     assert False
#

# def test_select_sets(test_grammar_simple):
#     table = LLTable(test_grammar_simple)
#     table.ComputeFirstSets()
#     table.ComputeFolowSets()
#     table.ComputeSelectSets()


def test_ll_table(test_grammar):
    table = LLTable(test_grammar)
    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    # table.ComputeTable()

def test_ll_predict(test_grammar):
    table = LLTable(test_grammar)
    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    table.ComputeTable()
    print(str(table.Predict(NonTerminal("factor"),LeftBracket())))
    assert False

# def test_ll_table_full():
#     table = LLTable(lumerical_grammar)
#     table.ComputeFirstSets()
#     print("--- Follow")
#     table.ComputeFolowSets()
#     table.ComputeSelectSets()
#     table.ComputeTable()
