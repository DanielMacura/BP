from queue import LifoQueue
from collections import deque
from typing import Deque
from lltable import LLTable
from symbol import Epsilon, NonTerminal, Terminal
from lex import Lexer
from grammar import Grammar
from tokens import EndOfFile, Token
from symbol import Action
from ast import AST, Module
import logging

logger = logging.getLogger(__name__)


class Parser:
    """The :py:class:`Parser` class handles the entire parsing process. Top-down parsing is handled by the provided LL table.

    :param grammar: The grammar according to which the LL table is constructed.
    :param lexer: The lexer provides a stream of tokens to be processed.
    :param table: The LL table.
    :param stack: The stack holds Terminals and NonTerminals, they are added and removed in a FIFO order. They guide the order of the parsing process.
    :param valueStack: The valueStack holds AST nodes, that have been encountederd and will be consumed by actions at a later point.
    :param tokenStack: The tokenStack holds already accepted tokens so they can be used in actions.
    :param ast: Stores the abstract syntax tree, used for resulting code generation.
    :param current_token: The current input token, call next(Lexer.tokens()) to update. 
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
        self.stack: LifoQueue[Terminal | NonTerminal | Action] = LifoQueue()
        self.valueStack: LifoQueue[AST] = LifoQueue()       # Stack for ast nodes
        self.valueStack.put(Module())
        self.tokenStack: LifoQueue[Token] = LifoQueue()     # Stack for tokens as input for actions
        self.ast = Module()
        self.stack.put(NonTerminal("body"))     # Stack for ll parsing

        self.current_token = next(self.lexer.tokens())
        logger.info("Initialized Parser")

    def parse(self):
        """This method runs the entire parsing process. A parse tree is generated uppon success.

        :raises TypeError: A incorrect object type was encountederd on the stack.
        """
        logger.info("START parsing")
        while not self.stack.empty():
            top = self.stack.get()
            logger.debug(
                f"Current iteration, top {top}, input token {self.current_token}"
            )
            logger.debug(f"Queue {list(self.stack.queue)}")
            logger.debug(f"valueStack {list(self.valueStack.queue)}\n\n")
            match top:
                # case Action(): # TBD if used
                #    pass
                case NonTerminal():
                    self.handleNonTerminal(top)

                case Terminal():
                    self.handleTerminal(top)

                case Action():
                    self.handleAction(top)
                case _:
                    raise TypeError(
                        f"Wrong type of object found on stack, {top.__class__}"
                    )

    def handleNonTerminal(self, top: NonTerminal):
        what_to_push = self.table.Predict(top, self.current_token)
        if what_to_push is None:
            logger.error(f"Failed parsing input, {top, self.current_token}")
            raise ValueError(
                f"Failed parsing input NonTerminal, failed at {top, self.current_token}"
            )
        if what_to_push.RHS == Epsilon():
            return
        logger.debug(f"Pushing {list(reversed(what_to_push.RHS))}")
        for symbol in reversed(what_to_push.RHS):
            self.stack.put(symbol)

    def handleTerminal(self, top: Terminal):
        if top == self.current_token:
            self.tokenStack.put(self.current_token)
            if self.current_token != EndOfFile():
                self.current_token = next(self.lexer.tokens())
        else:
            logger.error(f"Failed parsing input Terminal, {top, self.current_token}")
            raise ValueError(
                f"Cannont parse input, failed at {top, self.current_token}"
            )

    def handleAction(self, top: Action):
        logger.debug(f"Applying action {type(top).__name__}")
        top.call(self.valueStack, self.tokenStack)
