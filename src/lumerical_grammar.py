from symbol import Epsilon, NonTerminal
from tokens import *
from grammar import Grammar, Production

lumerical_grammar = Grammar()

body = NonTerminal("body")
nested_body = NonTerminal("nested_body")
function = NonTerminal("function")
statement = NonTerminal("statement")
identifier_action = NonTerminal("identifier_action")
assignment = NonTerminal("assignment")
function_call = NonTerminal("function_call")
parameter_list = NonTerminal("parameter_list")
parameter_list_prime = NonTerminal("parameter_list_prime")
argument_list = NonTerminal("argument_list")
argument_list_prime = NonTerminal("argument_list_prime")
control_structure = NonTerminal("control_structure")
elseNT = NonTerminal("else")
elifNT = NonTerminal("elif")
triple_argument_for = NonTerminal("triple_argument_for")

    

lumerical_grammar.append(Production(body, [statement, body]))
lumerical_grammar.append(Production(body, [function, body]))
lumerical_grammar.append(
    Production(
        function,
        [
            Function(),
            Identifier(),
            LeftBracket(),
            parameter_list,
            RightBracket(),
            LeftCurly(),
            nested_body,
            RightCurly(),
        ],
    )
)
lumerical_grammar.append(Production(body, Epsilon()))

lumerical_grammar.append(
    Production(
        nested_body,
        [statement, nested_body],
    )
)

lumerical_grammar.append(Production(nested_body, Epsilon()))

lumerical_grammar.append(Production(statement, [Identifier(), identifier_action]))
lumerical_grammar.append(Production(statement, [control_structure]))
lumerical_grammar.append(Production(identifier_action, [assignment]))
lumerical_grammar.append(Production(identifier_action, [function_call]))
lumerical_grammar.append(Production(assignment, [Equal(), Expression(), Semicolon()]))
lumerical_grammar.append(
    Production(
        function_call, [LeftBracket(), parameter_list, RightBracket(), Semicolon()]
    )
)
lumerical_grammar.append(
    Production(
        parameter_list,
        [Identifier(), parameter_list_prime],
    )
)
lumerical_grammar.append(Production(parameter_list, Epsilon()))
lumerical_grammar.append(
    Production(
        parameter_list_prime,
        [Comma(), Identifier(), parameter_list_prime],
    )
)
lumerical_grammar.append(Production(parameter_list_prime, Epsilon()))
lumerical_grammar.append(
    Production(
        argument_list,
        [Expression(), argument_list_prime],
    )
)
lumerical_grammar.append(Production(argument_list, Epsilon()))
lumerical_grammar.append(
    Production(
        argument_list_prime,
        [Comma(), Expression(), argument_list_prime],
    )
)

lumerical_grammar.append(Production(argument_list_prime, Epsilon()))
lumerical_grammar.append(
    Production(
        control_structure,
        [
            If(),
            LeftBracket(),
            Expression(),
            RightBracket(),
            LeftCurly(),
            nested_body,
            RightCurly(),
            elseNT,
        ],
    )
)
lumerical_grammar.append(
    Production(
        control_structure,
        [
            For(),
            LeftBracket(),
            Identifier(),
            assignment,
            Expression(),
            triple_argument_for,
            RightBracket(),
            LeftCurly(),
            nested_body,
            RightCurly(),
        ],
    )
)
lumerical_grammar.append(
    Production(
        elseNT,
        [Else(), elifNT, LeftCurly(), nested_body, RightCurly()],
    )
)
lumerical_grammar.append(Production(elseNT, Epsilon()))
lumerical_grammar.append(
    Production(
        elifNT,
        [If(), LeftBracket(), Expression(), RightBracket()],
    )
)
lumerical_grammar.append(Production(elifNT, Epsilon()))
lumerical_grammar.append(
    Production(
        triple_argument_for,
        [Semicolon(), Expression(), Semicolon(), Identifier(), assignment],
    )
)
lumerical_grammar.append(Production(triple_argument_for, Epsilon()))
