from lex import Lexer
print("LUMEX")

lex = Lexer("x= 3 + 1\n?x")
for token in lex.tokens():
    print(token)
