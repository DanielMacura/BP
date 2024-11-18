from queue import Queue
from lltable import LLTable
from symbol import Epsilon, NonTerminal, Terminal
from lumerical_grammar import body
from lex import Lexer
from grammar import Grammar


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

        self.stack: Queue[Terminal | NonTerminal] = Queue()
        self.ast = body
        self.stack.put(self.ast)

    def parse(self):
        """This method runs the entire parsing process. A parse tree is returned uppon success.

        :raises TypeError: A incorrect object type was encountederd on the stack.
        """
        current_token = next(self.lexer.tokens())
        while not self.stack.empty():
            top = self.stack.get()
            print("Iteration", current_token, top)
            # If top is ACTION:
            match top:
                # case Action(): # TBD if used
                #    pass
                case NonTerminal():
                    self.ast
                    # if EXPRESSION : parse expression bottom up
                    what_to_push = self.table.Predict(top, current_token)
                    if what_to_push is None:
                        raise ValueError(f"Cannont parse input, failed at {top, current_token}")
                    print("pushing")
                    if what_to_push.RHS == Epsilon():
                        break
                    for symbol in what_to_push.RHS:
                        print(symbol)
                        self.stack.put(symbol)

                case Terminal():
                    if top == current_token:
                        
                        try:
                            current_token = next(self.lexer.tokens())
                        except StopIteration:
                            print("Success!")
                            return
                    else:
                        raise ValueError(f"Cannont parse input, failed at {top, }")
                case _:
                    raise TypeError(
                        f"Wrong type of object found on stack, {top.__class__}"
                    )
