from pprint import pprint
from typing import TypeAlias
from grammar import Grammar, Production
from symbol import Epsilon, NonTerminal
from tokens import Integer, LeftBracket, Multiply, Plus, RightBracket, Semicolon, Token
from lltable import LLTable
import pytest
from copy import deepcopy
from lumerical_grammar import lumerical_grammar

@pytest.fixture
def test_grammar() -> Grammar:
    """
    #TODO Cite me - Alan Holub
    """
    Production.number = 0 # Hack to always get production numbering from 
    stmt = NonTerminal("stmt")
    expr = NonTerminal("expr")
    expr_p = NonTerminal("expr_p")
    term = NonTerminal("term")
    term_p = NonTerminal("term_p")
    factor = NonTerminal("factor")

    test_grammar = deepcopy(Grammar())

    test_grammar.append(Production(stmt, [expr, Semicolon()]))
    test_grammar.append(Production(expr, [term, expr_p]))
    test_grammar.append(Production(expr, Epsilon()))
    test_grammar.append(Production(expr_p, [Plus(), term, expr_p]))
    test_grammar.append(Production(expr_p, Epsilon()))
    test_grammar.append(Production(term, [factor, term_p]))
    test_grammar.append(Production(term_p, [Multiply(), factor, term_p]))
    test_grammar.append(Production(term_p, Epsilon()))
    test_grammar.append(Production(factor, [LeftBracket(), expr, RightBracket()]))
    test_grammar.append(Production(factor, [Integer()]))
    return deepcopy(test_grammar)


@pytest.fixture(autouse=True)
def test_grammar_simple() -> Grammar:
    """
    #TODO Cite me - Alan Holub
    """
    Production.number = 0 # Hack to always get production numbering from 
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


def test_first_sets(test_grammar):
    table = LLTable(test_grammar)

    table.ComputeFirstSets()
    assert table.firstSets == {
        NonTerminal(name="stmt"): {Integer(), Semicolon(), LeftBracket()},
        NonTerminal(name="expr"): {Integer(), LeftBracket()},
        NonTerminal(name="expr_p"): {Plus()},
        NonTerminal(name="term"): {Integer(), LeftBracket()},
        NonTerminal(name="term_p"): {Multiply()},
        NonTerminal(name="factor"): {Integer(), LeftBracket()},
    }


def test_follow_sets(test_grammar):
    table = LLTable(test_grammar)

    table.ComputeFirstSets()
    table.ComputeFolowSets()
    print(table.followSets)
    assert table.followSets == {
        NonTerminal(name="stmt"): set(),
        NonTerminal(name="expr"): {Semicolon(), RightBracket()},
        NonTerminal(name="expr_p"): {Semicolon(), RightBracket()},
        NonTerminal(name="term"): {Semicolon(), RightBracket(), Plus()},
        NonTerminal(name="term_p"): {Semicolon(), RightBracket(), Plus()},
        NonTerminal(name="factor"): {Semicolon(), Multiply(), Plus(), RightBracket()},
    }


def test_select_sets(test_grammar_simple):
    table = LLTable(test_grammar_simple)

    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    # assert table.selectSets == []


def test_ll_table(test_grammar):
    table = LLTable(test_grammar)

    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    table.ComputeTable()

    # assert table.table == []

def test_table_csv(test_grammar_simple):
    Production.number = 0
    table = LLTable(test_grammar_simple)

    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    table.ComputeTable()
    print()
    print()
    print()
    print()
    print(table)
    assert str(table) == ",ADM3,Perkin_Elmer,VT100,VT52\ndec_term, , ,5,4,\nstmt,2,1,3,3,\n"
def test_table_str():
    Production.number = 0
    table = LLTable(lumerical_grammar)

    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    table.ComputeTable()
    print()
    print()
    print()
    print()
    print()
    print("First")
    pprint(table.firstSets)
    print("followSets")
    pprint(table.followSets)
    print(table)
    print(lumerical_grammar)
    # assert False

def test_ll_predict(test_grammar):
    table = LLTable(test_grammar)
    table.ComputeFirstSets()
    table.ComputeFolowSets()
    table.ComputeSelectSets()
    table.ComputeTable()
    print(str(table.Predict(NonTerminal("factor"), LeftBracket())))


# def test_ll_table_full():
#     table = LLTable(lumerical_grammar)
#     table.ComputeFirstSets()
#     print("--- Follow")
#     table.ComputeFolowSets()
#     table.ComputeSelectSets()
#     table.ComputeTable()
