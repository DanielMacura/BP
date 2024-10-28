from symbol import Terminal


class Token(Terminal):
    """Tokens a are specific implementations of :py:class:`Terminal`.

    :param line_no: Line number of source code where the token was found.
    :param lexeme: Lexeme generating the token.
    :param lexeme_pattern: Regex pattern that represents the token.
    """

    def __init__(self):
        self.line_no: None | int = None
        self.lexeme: None | str = None
        self.lexeme_pattern: None | str = None

    def __str__(self) -> str:
        return self.__class__.__name__ + ":" + self.lexeme if self.lexeme else self.__class__.__name__


class Literal(Token):
    """A special :py:class:`Token` that also stores a value generated from it's lexeme.

    :param value:
    """

    def __init__(self):
        super().__init__()
        self.value = None

    def __str__(self) -> str:
        return self.__class__.__name__

class Identifier(Literal):
    pass


class Integer(Literal):
    pass


class Float(Literal):
    pass


class String(Literal):
    pass


class Variable(Literal):
    pass


# Mathematical operators
class Plus(Token):
    pass


class Minus(Token):
    pass


class Divide(Token):
    pass


class Multiply(Token):
    pass


# Comparison
class Equal(Token):
    pass


class NotEqual(Token):
    pass


class DoubleEqual(Token):
    pass


class GT(Token):
    pass


class GTE(Token):
    pass


class LT(Token):
    pass


class LTE(Token):
    pass


# Brackets
class LeftBracket(Token):
    pass


class RightBracket(Token):
    pass


class LeftCurly(Token):
    pass


class RightCurly(Token):
    pass


# Special characters
class EOF(Token):
    pass


class Comment(Literal):
    pass


class Questionmark(Token):
    pass


class Semicolon(Token):
    pass


class Comma(Token):
    pass


# Whitespace
class Space(Token):
    pass


class NewLine(Token):
    pass


# Keywords
class Function(Token):
    pass


class For(Token):
    pass


class If(Token):
    pass


class Else(Token):
    pass
