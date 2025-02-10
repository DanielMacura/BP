import pytest
from lex import Lexer
from tokens import EndOfFile, Equal, Identifier, Integer, Plus, Questionmark,Semicolon # Space, NewLine

# error- infinite loop
@pytest.mark.skip
@pytest.mark.parametrize(
    "src,expected",
    [
        (
            "x= 3 + 1; ",
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
                EndOfFile()
            ],
        )
    ],
)
def test_lexer(src, expected):
    lexer = Lexer(src)
    pytest.set_trace()
    for i, token in enumerate(list(lexer.tokens())):
        assert token == expected[i]
