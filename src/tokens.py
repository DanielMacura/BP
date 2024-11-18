from symbol import Terminal


class Token(Terminal):
    """Tokens a are specific implementations of :py:class:`Terminal`.

    :param line_no: Line number of source code where the token was found.
    :param lexeme: Lexeme generating the token.
    :param lexeme_pattern: Regex pattern that represents the token.
    """

    lexeme_pattern: str

    def __init__(self):
        self.line_no: None | int = None
        self.lexeme: None | str = None

    def __str__(self) -> str:
        return self.__class__.__name__

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


class Literal(Token):
    """A special :py:class:`Token` that also stores a value generated from it's lexeme.

    :param value:
    """

    def __init__(self, lexeme:str|None=None):
        super().__init__()
        self.value = None
        self.lexeme = lexeme

    def __str__(self) -> str:
        return (
            self.__class__.__name__ + ":" + self.lexeme
            if self.lexeme
            else self.__class__.__name__
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


class Expression(Token):
    lexeme_pattern = r""


class Identifier(Literal):
    lexeme_pattern = r"[A-Za-z][A-Za-z0-9]*"


class Integer(Literal):
    lexeme_pattern = r"[0-9]+"


class Float(Literal):
    lexeme_pattern = r"[0-9]\.[0-9]+"


class String(Literal):
    lexeme_pattern = r'"(?:\\"|[^"])*"'


# Mathematical operators
class Plus(Token):
    lexeme_pattern = r"\+"


class Minus(Token):
    lexeme_pattern = r"-"


class Divide(Token):
    lexeme_pattern = r"\\"


class Multiply(Token):
    lexeme_pattern = r"\*"


# Comparison
class Equal(Token):
    lexeme_pattern = r"\="


class NotEqual(Token):
    lexeme_pattern = r"\!\="


class DoubleEqual(Token):
    lexeme_pattern = r"\=\="


class GT(Token):
    lexeme_pattern = r"\>"


class GTE(Token):
    lexeme_pattern = r"\>\="


class LT(Token):
    lexeme_pattern = r"\<"


class LTE(Token):
    lexeme_pattern = r"\<\="


# Brackets
class LeftBracket(Token):
    lexeme_pattern = r"\("


class RightBracket(Token):
    lexeme_pattern = r"\)"


class LeftCurly(Token):
    lexeme_pattern = r"\{"


class RightCurly(Token):
    lexeme_pattern = r"\}"


# Special characters
# class EOF(Token):
#     pass
#
#
# class Comment(Literal):
#     pass


class Questionmark(Token):
    lexeme_pattern = r"\?"


class Semicolon(Token):
    lexeme_pattern = r"\;"


class Comma(Token):
    lexeme_pattern = r"\,"


# Whitespace
class Space(Token):
    lexeme_pattern = r"[\t ]+"


class NewLine(Token):
    lexeme_pattern = r"\r?\n"


# Keywords
class Function(Token):
    lexeme_pattern = r"function"


class For(Token):
    lexeme_pattern = r"for"


class If(Token):
    lexeme_pattern = r"if"


class Else(Token):
    lexeme_pattern = r"else"
