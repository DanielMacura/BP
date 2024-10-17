import re
from tokens import * 
from grammar import expressions
    

class Lexer():
    def __init__(self, source:str):
        print("lexer innit")
        self.cursor:int = 0
        self.source:str = source
        print(self.source)
        self.parse()
        
    def advance(self) -> Token|None:
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

    def parse(self):
        while True:
            token = self.advance()
            print(token)
            if not token:
                break

