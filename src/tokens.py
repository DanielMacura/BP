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

    def __init__(self, lexeme: str | None = None):
        super().__init__()
        self.value = None
        self.lexeme = lexeme

    def __str__(self) -> str:
        return self.__class__.__name__
        return (
            self.__class__.__name__ + ":" + self.lexeme
            if self.lexeme
            else self.__class__.__name__
        )

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


class Identifier(Literal):
    """
    Represents an identifier token (e.g., variable names).

    :param lexeme_pattern: The regular expression pattern used to match an identifier,
                            which starts with a letter and can be followed by letters and digits.
                            Lexeme pattern: `r"[A-Za-z][A-Za-z0-9]*"`
    """

    lexeme_pattern = r"[A-Za-z][A-Za-z0-9]*"


class Integer(Literal):
    """
    Represents an integer literal token.

    :param lexeme_pattern: The regular expression pattern used to match an integer,
                            which consists of one or more digits.
                            Lexeme pattern: `r"[0-9]+"`
    """

    lexeme_pattern = r"[0-9]+"


class Float(Literal):
    """
    Represents a floating-point literal token.

    :param lexeme_pattern: The regular expression pattern used to match a float,
                            which consists of a digit, a period, and one or more digits after the period.
                            Lexeme pattern: `r"[0-9].[0-9]+"`
    """

    lexeme_pattern = r"[0-9]\.[0-9]+"


class String(Literal):
    """
    Represents a string literal token.

    :param lexeme_pattern: The regular expression pattern used to match a string,
                            which starts and ends with a double quote and may contain escaped quotes.
                            Lexeme pattern: `r'"(?:"|[^"])*"'`
    """

    lexeme_pattern = r'"(?:\\"|[^"])*"'


# Mathematical operators
class Plus(Token):
    """
    Represents the '+' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the plus operator.
                            Lexeme pattern: `r"+"`
    """

    lexeme_pattern = r"\+"


class Minus(Token):
    """
    Represents the '-' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the minus operator.
                            Lexeme pattern: `r"-"`
    """

    lexeme_pattern = r"-"


class Divide(Token):
    """
    Represents the division operator token.

    :param lexeme_pattern: The regular expression pattern used to match the division operator.
                            Lexeme pattern: `r"/"`
    """

    lexeme_pattern = r"/"


class Multiply(Token):
    """
    Represents the multiplication operator token.

    :param lexeme_pattern: The regular expression pattern used to match the multiplication operator.
                            Lexeme pattern: `r"*"`
    """

    lexeme_pattern = r"\*"


class Not(Token):
    """
    Represents the unary not operator token.

    :param lexeme_pattern: The regular expression pattern used to match the unary not operator.
                            Lexeme pattern: `r"!"`
    """

    lexeme_pattern = r"\!"


# Comparison operators
class Equal(Token):
    """
    Represents the equality operator token.

    :param lexeme_pattern: The regular expression pattern used to match the equality operator.
                            Lexeme pattern: `r"="`
    """

    lexeme_pattern = r"\="


class NotEqual(Token):
    """
    Represents the not-equal operator token.

    :param lexeme_pattern: The regular expression pattern used to match the not-equal operator.
                            Lexeme pattern: `r"!="`
    """

    lexeme_pattern = r"\!\="


class DoubleEqual(Token):
    """
    Represents the double equality operator token.

    :param lexeme_pattern: The regular expression pattern used to match the double equal operator.
                            Lexeme pattern: `r"=="`
    """

    lexeme_pattern = r"\=\="


class GT(Token):
    """
    Represents the 'greater than' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the 'greater than' operator.
                            Lexeme pattern: `r">"`
    """

    lexeme_pattern = r"\>"


class GTE(Token):
    """
    Represents the 'greater than or equal to' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the 'greater than or equal to' operator.
                            Lexeme pattern: `r">="`
    """

    lexeme_pattern = r"\>\="


class LT(Token):
    """
    Represents the 'less than' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the 'less than' operator.
                            Lexeme pattern: `r"<"`
    """

    lexeme_pattern = r"\<"


class LTE(Token):
    """
    Represents the 'less than or equal to' operator token.

    :param lexeme_pattern: The regular expression pattern used to match the 'less than or equal to' operator.
                            Lexeme pattern: `r"<="`
    """

    lexeme_pattern = r"\<\="


# Brackets
class LeftBracket(Token):
    """
    Represents the left parenthesis '(' token.

    :param lexeme_pattern: The regular expression pattern used to match the left parenthesis.
                            Lexeme pattern: `r"("`
    """

    lexeme_pattern = r"\("


class RightBracket(Token):
    """
    Represents the right parenthesis ')' token.

    :param lexeme_pattern: The regular expression pattern used to match the right parenthesis.
                            Lexeme pattern: `r")"`
    """

    lexeme_pattern = r"\)"


class LeftCurly(Token):
    """
    Represents the left curly brace '{' token.

    :param lexeme_pattern: The regular expression pattern used to match the left curly brace.
                            Lexeme pattern: `r"{"`
    """

    lexeme_pattern = r"\{"


class RightCurly(Token):
    """
    Represents the right curly brace '}' token.

    :param lexeme_pattern: The regular expression pattern used to match the right curly brace.
                            Lexeme pattern: `r"}"`
    """

    lexeme_pattern = r"\}"


# Special characters
class Questionmark(Token):
    """
    Represents the '?' token.

    :param lexeme_pattern: The regular expression pattern used to match the question mark.
                            Lexeme pattern: `r"?"`
    """

    lexeme_pattern = r"\?"


class Semicolon(Token):
    """
    Represents the semicolon ';' token.

    :param lexeme_pattern: The regular expression pattern used to match the semicolon.
                            Lexeme pattern: `r";"`
    """

    lexeme_pattern = r"\;"


class Colon(Token):
    """
    Represents the colon ':' token.

    :param lexeme_pattern: The regular expression pattern used to match the colon.
                            Lexeme pattern: `r":"`
    """

    lexeme_pattern = r"\:"


class Comma(Token):
    """
    Represents the comma ',' token.

    :param lexeme_pattern: The regular expression pattern used to match the comma.
                            Lexeme pattern: `r","`
    """

    lexeme_pattern = r"\,"


# Whitespace
class Space(Token):
    """
    Represents whitespace characters (spaces and tabs).

    :param lexeme_pattern: The regular expression pattern used to match spaces and tabs.
                            Lexeme pattern: `r"[\\t ]+"`
    """

    lexeme_pattern = r"[\t ]+"


class NewLine(Token):
    """
    Represents newline characters.

    :param lexeme_pattern: The regular expression pattern used to match newline characters.
                            Lexeme pattern: `r"\\r?\\n"`
    """

    lexeme_pattern = r"\r?\n"

class EndOfFile(Token):
    """
    Represents a EOF token at the end of the parsed file. Used to terminate parsing process.

    :param lexeme_pattern: The regular expression pattern used to match the end of a file.
                            Lexeme pattern: `r"\\Z"`
    """

    lexeme_pattern = r"\Z"

# Keywords
class Function(Token):
    """
    Represents the 'function' keyword.

    :param lexeme_pattern: The regular expression pattern used to match the 'function' keyword.
                            Lexeme pattern: `r"function"`
    """

    lexeme_pattern = r"function"


class For(Token):
    """
    Represents the 'for' keyword.

    :param lexeme_pattern: The regular expression pattern used to match the 'for' keyword.
                            Lexeme pattern: `r"for"`
    """

    lexeme_pattern = r"for"

class Break(Token):
    """
    Represents the 'break' keyword.

    :param lexeme_pattern: The regular expression pattern used to match the 'break' keyword.
                            Lexeme pattern: `r"break"`
    """

    lexeme_pattern = r"break"

class If(Token):
    """
    Represents the 'if' keyword.

    :param lexeme_pattern: The regular expression pattern used to match the 'if' keyword.
                            Lexeme pattern: `r"if"`
    """

    lexeme_pattern = r"if"


class Else(Token):
    """
    Represents the 'else' keyword.

    :param lexeme_pattern: The regular expression pattern used to match the 'else' keyword.
                            Lexeme pattern: `r"else"`
    """

    lexeme_pattern = r"else"

