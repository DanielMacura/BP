import pytest
from lex import Lexer
from tokens import Equal, Identifier, Integer, Plus, Questionmark,Semicolon # Space, NewLine


@pytest.mark.parametrize(
    "src,expected",
    [
        (
            "x= 3 + 1;\n?x",
            [
                Identifier("x"),
                Equal(),
                # Space(),
                Integer("3"),
                # Space(),
                Plus(),
                # Space(),
                Integer("1"),
                Semicolon(),
                # NewLine(),
                Questionmark(),
                Identifier("x"),
            ],
        )
    ],
)
def test_lexer(src, expected):
    lexer = Lexer(src)

    for i, token in enumerate(list(lexer.tokens())):
        assert token == expected[i]
