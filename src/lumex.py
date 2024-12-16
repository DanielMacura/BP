from lex import Lexer
from parse import Parser
from lumerical_grammar import lumerical_grammar

print("LUMEX")


# lexer = Lexer("x(a,b,c)")
lexer = Lexer("x=3+1;")
parser = Parser(lumerical_grammar, lexer)
parser.parse()
