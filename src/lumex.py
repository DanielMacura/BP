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
    # lexer = Lexer("if( 3<x< 5 and x ==4 ) { y = 2; } ")
    # lexer = Lexer("if( x< 5) { y = 2; } else if (x>3){ y = 1 ; x = 11; if(x > 5){?x;}} else if (x>30){ y = 10 ;} else {y = 0;} ")
    # lexer = Lexer("y=5;\n for(x=-1:-2:-10) {y = 1;}")
    # lexer = Lexer("y=5;\n for(x=1:10) {y = 1;}")
    # lexer = Lexer("for(x=1;x>10;x=x+1){y=1;}")
    # lexer = Lexer("for(x=1:2:10){?x+1; if(x==5){x = 4;}}")
    # lexer = Lexer("for(x=1:2:10){x=x+3; ?x+1; break;}")
    # lexer = Lexer("addfdtd;")
    # lexer = Lexer('addrect;')
    # lexer = Lexer('addfdtd;\naddrect;\naddrect;\nset("name", "block");')
    # lexer = Lexer('addfdtd;\naddrect;\naddrect;\nset("name", "block");\nset("x", 5);')
    # lexer = Lexer('addfdtd;\naddrect;\naddrect;\nset("name", "block");\nset("x", 5);\nset("x span", 7);\nset("z span", 11);')
    # lexer = Lexer('addfdtd;\naddrect;\naddrect;\nset("name", "block");\nset("x", 5);\nset("x span", 7);\nselectall;\nset("z span", 11);')
    # lexer = Lexer('addfdtd;\naddrect;\naddrect;\nset("name", "block");\nset("x", 5);\nset("x span", 7);\nshiftselect("Rectangle");\nset("z span", 11);\nselect("block");\nset("z", 2+2);')
    # lexer = Lexer('addfdtd;\naddplane;\nset("frequency", 1e9)')
    lexer = Lexer('addfdtd;\nset("dimension", 2);')
    # lexer = Lexer('addfdtd;\nset("x span", 7);')


    parser = Parser(lumerical_grammar, lexer)
    parser.parse()
    tree = parser.valueStack.get()
    tree = ast.fix_missing_locations(tree) 
    logger.info("Python AST dump\n" + ast.dump(tree, indent=4) + "\n")
    logger.info("Lumerical source\n" + lexer.source + "\n")
    logger.info("Transpiled Python\n" + ast.unparse(ast.fix_missing_locations(tree)) + "\n")

    logger.info("SUCCESS LUMEX")
    print(ast.unparse(ast.fix_missing_locations(tree)))


if __name__ == "__main__":
    main()
