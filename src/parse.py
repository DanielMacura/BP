from operator import contains
from queue import LifoQueue
from collections import deque
from typing import Deque
from lltable import LLTable
from symbol import Epsilon, NonTerminal, Terminal
from lumerical_grammar import body
from lex import Lexer
from grammar import Grammar
from tokens import Token
from precedence_table import PrecedenceTable, Action
import pytest

class Parser:
    """The :py:class:`Parser` class handles the entire parsing process. Top-down parsing is handles by the provided LL table.
    When an expression is encountered, the parser switches to bottom-up precedence parsing.

    :param grammar: The grammar according to which the LL table is constructed.
    :param lexer: The lexer provides a stream of tokens to be processed.
    :param table: The LL table.
    :param stack: The stack holds Terminals and NonTerminals, they are added and removed in a FIFO order. They guide the order of the parsing process.
    """

    def __init__(self, grammar: Grammar, lexer: Lexer) -> None:
        """The :py:class:`Parser` constructor.

        :param grammar: The grammar according to which the input should be parsed.
        :param lexer: The :py:class:`Lexer` provides the stream of tokens to be parsed.
        """
        self.grammar = grammar
        self.lexer = lexer
        self.table = LLTable(self.grammar)
        self.table.ComputeTable()
        self.precedence_table = PrecedenceTable()
        self.precedence_stack: Deque[Token | NonTerminal | Action] = deque()
        self.stack: LifoQueue[Terminal | NonTerminal] = LifoQueue()
        self.ast = NonTerminal("body")
        self.stack.put(NonTerminal("body"))

        self.current_token = next(self.lexer.tokens())

    def parse(self):
        """This method runs the entire parsing process. A parse tree is returned uppon success.

        :raises TypeError: A incorrect object type was encountederd on the stack.
        """
        while not self.stack.empty():
            top = self.stack.get()
            print("Iteration", top, self.current_token)
            print("queue", list(self.stack.queue))
            match top:
                # case Action(): # TBD if used
                #    pass
                case NonTerminal():
                    self.ast
                    what_to_push = self.table.Predict(top, self.current_token)
                    if what_to_push is None:
                        raise ValueError(
                            f"Cannont parse input, failed at {top, self.current_token}"
                        )
                    print("pushing")
                    if what_to_push.RHS == Epsilon():
                        continue
                    for symbol in reversed(what_to_push.RHS):
                        print(symbol)
                        self.stack.put(symbol)

                case Terminal():
                    if top == self.current_token:
                        try:
                            self.current_token = next(self.lexer.tokens())
                        except StopIteration:
                            print("Success!")
                            return
                    else:
                        raise ValueError(f"Cannont parse input, failed at {top, }")
                case _:
                    raise TypeError(
                        f"Wrong type of object found on stack, {top.__class__}"
                    )

    def top(self) -> tuple[None | Token, int]:
        """Return the topmost terminal on the stack.
        If the stack contains no terminals, None is returned instead.

        :param stack: Stack to be iterated over.
        :return: Topmost terminal on stack.
        """
        for i in range(len(self.precedence_stack)):
            if isinstance(self.precedence_stack[i], Terminal):
                return self.precedence_stack[i], i
        return None, -1

    def parseBottomUp(self):
        while True:
            top, top_index = self.top()
            precedence = self.precedence_table.getPrecedence(top, self.current_token)

            

            match precedence:
                case Action.SHIFT_EQ:
                    self.precedence_stack.append(self.current_token)
                    self.current_token = next(self.lexer.tokens())
                case Action.SHIFT_LT:
                    self.precedence_stack.insert(top_index, Action.SHIFT_LT)
                    self.precedence_stack.append(self.current_token)
                    self.current_token = next(self.lexer.tokens())

                case Action.REDUCE:
                    nonterminal = self.precedence_stack.pop()
                    if not isinstance(nonterminal, NonTerminal):
                        raise ValueError(f"Wrong symbol on top of precedence stack, found {nonterminal}.")
                    
