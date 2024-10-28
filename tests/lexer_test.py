from lex import Lexer

def test_lexer():
    lex = Lexer("x= 3 + 1\n?x")
    for token in lex.tokens():
        print(token)
    assert False
