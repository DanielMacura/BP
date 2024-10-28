import re
from tokens import * 
from token_rules import expressions
from typing_extensions import Generator
    

class Lexer():
    """The Lexer class is responsible for, lexing, splitting up the input stream into tokens. Individual tokens
    are defined in :py:mod:`tokens`, the rules for which lexemes belong to tokens are defined in :py:mod:`grammar`.
    
    :param cursor: Used to remember which part of the source was already lexed.
    :param source: The source code.
    """

    def __init__(self, source:str):
        
        """

        :param source: The source code to be lexed.
        """
        print("lexer innit")
        self.cursor:int = 0
        self.source:str = source
        print(self.source)
        
    def advance(self) -> Token|None:
        """Advances and tries to math the next token from the remaining source. The longest lexeme matching a rule from :py:mod:`grammar`,
        is converted it's respectful token and it's lexeme is assigned.

        :return: Token if sucessfuly parsed, None when there are no more tokens to produce.
        """
        longestMatch = None
        longestMatchToken = None
        for expression in expressions:
            pattern, expressionToken = expression
            regex = re.compile(pattern)
            match = regex.match(self.source, self.cursor)
            if match:
                if longestMatch is None or match.end(0) > longestMatch.end(0):
                    longestMatch = match
                    token:Token = expressionToken()
                    token.lexeme = longestMatch.group(0)
                    longestMatchToken = token
        if longestMatch is not None:
            self.cursor = longestMatch.end(0)
        return longestMatchToken

    def tokens(self) -> Generator[Token,None,None]:

        """A generator that returns the next token. Calls :py:meth:`advance` until it returns None.

        :return: All tokens.
        """
        token = self.advance()
        while token:
            yield token
            token = self.advance()

