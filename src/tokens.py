class Token():
    def __init__(self):
        self.line_no:None|int = None
        self.lexeme:None|str = None
    def __repr__(self) -> str:
        return self.__class__.__name__ + ":" + self.lexeme if self.lexeme else "" 
    
class Literal(Token):
    def __init__(self):
        super().__init__()
        self.value = None


class Integer(Literal):
    pass
class Float(Literal):
    pass
class String(Literal):
    pass
class Symbol(Literal):
    pass

# Mathematical operators
class Plus(Literal):
    pass
class Minus(Literal):
    pass
class Divide(Literal):
    pass
class Multiply(Literal):
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

# Special characters
class Comment(Literal):
    pass
class Questionmark(Token):
    pass

# Whitespace
class Space(Token):
    pass
class NewLine(Token):
    pass
