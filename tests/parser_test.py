import pytest
from lex import Lexer
from parse import Parser
from lumerical_grammar import lumerical_grammar
import ast


@pytest.mark.parametrize(
    "input,output",
    [
        ("x = 1;", "x = 1"),
        ("x=x;", "x = x"),
        ("x = y;", "x = y"),
        ("x = -5;", "x = -5"),
        ("x = 1 <= 4 < 5 == 2 > 1 >= 1;", "x = 1 <= 4 < 5 == (2 > 1 >= 1)"),
    ],
)
def test_assignment(input, output):
    lexer = Lexer(input)

    parser = Parser(lumerical_grammar, lexer)
    parser.parse()
    tree = parser.valueStack.get()
    ast.fix_missing_locations(tree)

    print(ast.unparse(tree))
    assert ast.unparse(tree) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("if (x == 1) {x = 2;}", "if x == 1:\n    x = 2"),
        (
            "if (x == 1) {x = 2;} else {x = 1;}",
            "if x == 1:\n    x = 2\nelse:\n    x = 1",
        ),
        (
            "if (x == 1) {x = 2;} else if (x == 2) {x = 0;} else {x = 1;}",
            "if x == 1:\n    x = 2\nelif x == 2:\n    x = 0\nelse:\n    x = 1",
        ),
    ],
)
def test_if_statements(input, output):
    lexer = Lexer(input)

    parser = Parser(lumerical_grammar, lexer)
    parser.parse()
    tree = parser.valueStack.get()
    ast.fix_missing_locations(tree)

    print(ast.unparse(tree))
    assert ast.unparse(tree) == output

@pytest.mark.parametrize(
    "input,output",
    [
        ("for(x=-1:-2:-10) {y=1;}", "x = -1\nwhile x >= -10:\n    y = 1\n    x += -2"),
        ("for(x=1:10) {y=1;}", "x = 1\nwhile x <= 10:\n    y = 1\n    x += 1"),
        ("for(x=1:10) {for(z=2:5) {y=1;}}", "x = 1\nwhile x <= 10:\n    z = 2\n    while z <= 5:\n        y = 1\n        z += 1\n    x += 1"),

    ],
)
def test_for_statements(input, output):
    lexer = Lexer(input)

    parser = Parser(lumerical_grammar, lexer)
    parser.parse()
    tree = parser.valueStack.get()
    ast.fix_missing_locations(tree)

    print(ast.unparse(tree))
    assert ast.unparse(tree) == output
