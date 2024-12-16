
from collections import deque
from typing import Deque
from lex import Lexer
from precedence_table import PrecedenceTable, Action
from symbol import Terminal, NonTerminal

class PrecedenceParser():
    def __init__(self, lexer: Lexer) -> None:
        """The :py:class:`PrecedenceParser` constructor.
        """
        self.precedence_table = PrecedenceTable()
        self.stack: Deque[Terminal | NonTerminal | Action] = deque()
        self.lexer: Lexer = lexer

    def top(self) -> None|Terminal:
        """Return the topmost terminal on the stack.
        If the stack contains no terminals, None is returned instead.

        :param stack: Stack to be iterated over.
        :return: Topmost terminal on stack.
        """
        for i in range(len(self.stack)):
            if isinstance(self.stack[i], Terminal):
                return self.stack[i]
        return None

    def parseBottomUp(self):
        
        pass
