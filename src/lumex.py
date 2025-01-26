from ast import parse
from lex import Lexer
from parse import Parser
from lumerical_grammar import lumerical_grammar
import logging
import ast

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(filename="lumex.log", level=logging.DEBUG, filemode="w")
    logger.info("START LUMEX")

    # lexer = Lexer("x= 1<=12 <= 5 == 2 > 3;")
    # lexer = Lexer("x=-3;")
    # lexer = Lexer("if( 3<x< 5) { y = 2; } ")
    lexer = Lexer("if( x< 5) { y = 2; } else if (x>3){ y = 1 ;} else if (x>30){ y = 10 ;} else {y = 0;} ")

    parser = Parser(lumerical_grammar, lexer)
    parser.parse()
    tree = parser.valueStack.get()
    logger.info(ast.dump(tree, indent=4))
    ast.fix_missing_locations(tree)
    logger.info(ast.unparse(tree))

    logger.info("SUCCESS LUMEX")


if __name__ == "__main__":
    main()
