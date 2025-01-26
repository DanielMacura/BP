import re
import logging
from tokens import *
from typing_extensions import Generator

logger = logging.getLogger(__name__)


class Lexer:
    """The Lexer class is responsible for, lexing, splitting up the input stream into tokens. Individual tokens
    are defined in :py:mod:`tokens`, the rules for which lexemes belong to tokens are defined in :py:mod:`grammar`.

    :param cursor: Used to remember which part of the source was already lexed.
    :param source: The source code.
    """

    def __init__(self, source: str):
        """Lexer constructor, finds all tokens and creates a LUT.

        :param source: The source code to be lexed.
        """
        self.cursor: int = 0
        self.source: str = source
        self.token_lexeme_pairs = [
            (subclass.lexeme_pattern, subclass)
            for subclass in Token.__subclasses__() + Literal.__subclasses__()
            if subclass.__name__ != "Literal"
        ]
        logger.info("Initialized Lexer")

    def advance(self) -> Token | None:
        """Advances and tries to math the next token from the remaining source. The longest lexeme matching a rule from :py:mod:`grammar`,
        is converted it's respectful token and it's lexeme is assigned.

        :return: Token if sucessfuly parsed, None when there are no more tokens to produce.
        """
        longestMatch = None
        longestMatchToken = None
        for pair in self.token_lexeme_pairs:
            pattern, expressionToken = pair
            print(pair, self.source[self.cursor :], self.cursor)
            regex = re.compile(pattern)
            match = regex.match(self.source, self.cursor)
            if match:
                logger.debug(f"Matched {match.group(0)}")
                if longestMatch is None or match.end(0) > longestMatch.end(0):
                    logger.debug(f"So far longest match is {match.group(0)}")
                    longestMatch = match
                    token: Token = expressionToken()
                    token.lexeme = longestMatch.group(0)
                    longestMatchToken = token
        if longestMatch is not None:
            self.cursor = longestMatch.end(0)
        if longestMatchToken:
            logger.info(f"Advanced lexer with token {longestMatchToken} matching {longestMatchToken.lexeme}")
        else:
            logger.warning("Did not match any token")
        return longestMatchToken

    def tokens(self) -> Generator[Token, None, None]:
        """A generator that returns the next token. Calls :py:meth:`advance` until it returns None.

        Whitespace tokens are ignored.

        :return: All tokens.
        """
        token = self.advance()
        while token:
            if token == Space() or token == NewLine():
                token = self.advance()
                continue
            yield token
            token = self.advance()
