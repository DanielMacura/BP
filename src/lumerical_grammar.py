import actions
import ast
from symbol import Epsilon, NonTerminal
from tokens import *
from grammar import Grammar, Production


lumerical_grammar = Grammar()

root = NonTerminal("root")
body = NonTerminal("body")
nested_body = NonTerminal("nested_body")
nested_else_body = NonTerminal("nested_else_body")
function = NonTerminal("function")
statement = NonTerminal("statement")
selection = NonTerminal("selection")
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
loop_condition = NonTerminal("loop_condition")
range_step = NonTerminal("range_step")

# Expressions

expression = NonTerminal("expression")
logic_and = NonTerminal("logic_and")
logic_and_prime = NonTerminal("logic_and_prime")
logic_or = NonTerminal("logic_or")
logic_or_prime = NonTerminal("logic_or_prime")
equality = NonTerminal("equality")
equality_prime = NonTerminal("equality_prime")
comparison = NonTerminal("comparison")
comparison_prime = NonTerminal("comparison_prime")
term = NonTerminal("term")
term_prime = NonTerminal("term_prime")
factor = NonTerminal("factor")
factor_prime = NonTerminal("factor_prime")
unary = NonTerminal("unary")
primary = NonTerminal("primary")

lumerical_grammar.append(Production(root, [actions.Imports(), actions.StoreToBody(), actions.CreateSelector(), actions.StoreToBody(), body]))

lumerical_grammar.append(Production(body, [statement, actions.StoreToBody(), body]))
lumerical_grammar.append(Production(body, [function, body, EndOfFile()]))
lumerical_grammar.append(Production(body, Epsilon()))
lumerical_grammar.append(Production(body, [EndOfFile()]))
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


lumerical_grammar.append(
    Production(
        nested_body,
        [statement, actions.StoreToBody(), nested_body],
    )
)

lumerical_grammar.append(Production(nested_body, Epsilon()))

lumerical_grammar.append(
    Production(
        nested_else_body,
        [statement, actions.StoreToElse(), nested_else_body],
    )
)

lumerical_grammar.append(Production(nested_else_body, Epsilon()))

lumerical_grammar.append(Production(statement, [Identifier(), actions.StoreVariableName(), identifier_action]))
lumerical_grammar.append(Production(statement, [control_structure]))
lumerical_grammar.append(Production(statement, [selection]))
lumerical_grammar.append(Production(statement, [Questionmark(), expression, actions.Print(), Semicolon()]))
lumerical_grammar.append(Production(statement, [AddFDTD(), actions.AddFDTD(), Semicolon()]))
lumerical_grammar.append(Production(statement, [AddRect(), actions.AddRect(), Semicolon()]))
lumerical_grammar.append(Production(statement, [AddSphere(), actions.AddSphere(), Semicolon()]))
lumerical_grammar.append(Production(statement, [AddPlane(), actions.AddPlaneSource(), Semicolon()]))
lumerical_grammar.append(Production(statement, [AddDFTMonitor(), actions.AddDFTMonitor(), Semicolon()]))
lumerical_grammar.append(Production(statement, [SetToken(), LeftBracket(), String(), actions.StoreLiteral("str"), Comma(), expression, actions.SetProperty(), RightBracket(), Semicolon()]))
lumerical_grammar.append(Production(statement, [Break(),actions.Break(), Semicolon()]))
lumerical_grammar.append(Production(selection, [SelectAll(),actions.SelectAll(), Semicolon()]))
lumerical_grammar.append(Production(selection, [UnselectAll(), actions.UnselectAll(), Semicolon()]))
lumerical_grammar.append(Production(selection, [Select(),LeftBracket(),String(),actions.StoreLiteral("str"),actions.Select(),RightBracket(), Semicolon()]))
lumerical_grammar.append(Production(selection, [ShiftSelect(),LeftBracket(),String(),actions.StoreLiteral("str"),actions.ShiftSelect(), RightBracket(), Semicolon()]))
lumerical_grammar.append(Production(identifier_action, [assignment]))
lumerical_grammar.append(Production(identifier_action, [function_call]))
lumerical_grammar.append(Production(assignment, [Equal(), expression, actions.AssignToVariable(), Semicolon()]))
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
        [expression, argument_list_prime],
    )
)
lumerical_grammar.append(Production(argument_list, Epsilon()))
lumerical_grammar.append(
    Production(
        argument_list_prime,
        [Comma(), expression, argument_list_prime],
    )
)

lumerical_grammar.append(Production(argument_list_prime, Epsilon()))
lumerical_grammar.append(
    Production(
        control_structure,
        [
            If(),
            LeftBracket(),
            expression,
            RightBracket(),
            LeftCurly(),
            actions.If(),
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
            actions.CreateEmptyWhile(),
            LeftBracket(),
            Identifier(),
            actions.StoreVariableName(),
            Equal(),
            expression,
            actions.AssignToVariable(),
            loop_condition,
            RightBracket(),
            LeftCurly(),
            nested_body,
            actions.HandleAllLoops(),
            RightCurly(),
        ]
    )
)

lumerical_grammar.append(
    Production(
        loop_condition,
        [
            Colon(),
            expression,
            actions.CreateRangeCondition(),
            range_step,
        ]
    )
)

lumerical_grammar.append(
    Production(
        range_step,
        [Colon(), expression, actions.ExtendRangeCondition()]
    )
)
lumerical_grammar.append(
    Production(
        range_step,
        Epsilon()
    )
)

lumerical_grammar.append(
    Production(
        loop_condition,
        [Semicolon(), expression, Semicolon(), expression, actions.CreateWhileCondition()]
    )
)

lumerical_grammar.append(
    Production(
        elseNT,
        [Else(), elifNT, LeftCurly(), actions.HandleElse(), nested_else_body,actions.CleanUpElse(), RightCurly(), elseNT],
    )
)
lumerical_grammar.append(Production(elseNT, Epsilon()))
lumerical_grammar.append(
    Production(
        elifNT,
        [If(), LeftBracket(), expression, RightBracket()],
    )
)
lumerical_grammar.append(Production(elifNT, Epsilon()))

# Expressions
lumerical_grammar.append(Production(expression, [logic_and]))
lumerical_grammar.append(Production(logic_and, [logic_or, logic_and_prime]))
lumerical_grammar.append(Production(logic_and_prime, [And(), equality, actions.LogicOperation(ast.And()), logic_and_prime]))
lumerical_grammar.append(Production(logic_and_prime, Epsilon()))
lumerical_grammar.append(Production(logic_or, [comparison, logic_or_prime]))
lumerical_grammar.append(Production(logic_or_prime, [Or(), equality, actions.LogicOperation(ast.Or()), logic_or_prime]))
lumerical_grammar.append(Production(logic_or_prime, Epsilon()))
lumerical_grammar.append(Production(equality, [comparison, equality_prime]))
lumerical_grammar.append(Production(equality_prime, [NotEqual(), comparison, actions.Comparison(ast.NotEq()), equality_prime]))
lumerical_grammar.append(Production(equality_prime, [DoubleEqual(), comparison, actions.Comparison(ast.Eq()), equality_prime]))
lumerical_grammar.append(Production(equality_prime, Epsilon()))
lumerical_grammar.append(Production(comparison, [term, comparison_prime]))
lumerical_grammar.append(Production(comparison_prime, [GT(), term, actions.Comparison(ast.Gt()), comparison_prime]))
lumerical_grammar.append(Production(comparison_prime, [GTE(), term, actions.Comparison(ast.GtE()), comparison_prime]))
lumerical_grammar.append(Production(comparison_prime, [LT(), term, actions.Comparison(ast.Lt()), comparison_prime]))
lumerical_grammar.append(Production(comparison_prime, [LTE(), term, actions.Comparison(ast.LtE()), comparison_prime]))
lumerical_grammar.append(Production(comparison_prime, Epsilon()))
lumerical_grammar.append(Production(term, [factor, term_prime]))
lumerical_grammar.append(Production(term_prime,[Minus(), factor,actions.BinaryOperation(ast.Sub()), term_prime]))
lumerical_grammar.append(Production(term_prime,[Plus(), factor, actions.BinaryOperation(ast.Add()), term_prime]))
lumerical_grammar.append(Production(term_prime,Epsilon()))
lumerical_grammar.append(Production(factor, [unary, factor_prime]))
lumerical_grammar.append(Production(factor_prime, [Divide(), unary, actions.BinaryOperation(ast.Div()), factor_prime]))
lumerical_grammar.append(Production(factor_prime, [Multiply(), unary, actions.BinaryOperation(ast.Mult()), factor_prime]))
lumerical_grammar.append(Production(factor_prime, Epsilon()))
lumerical_grammar.append(Production(unary, [Not(), unary]))
lumerical_grammar.append(Production(unary, [Minus(), unary, actions.UnarySubtract()]))
lumerical_grammar.append(Production(unary, [primary]))
lumerical_grammar.append(Production(primary, [Integer(), actions.StoreLiteral("int")]))
lumerical_grammar.append(Production(primary, [Float(), actions.StoreLiteral("float")]))
lumerical_grammar.append(Production(primary, [String(), actions.StoreLiteral("str")]))
lumerical_grammar.append(Production(primary, [Identifier(), actions.StoreVariableName()]))
lumerical_grammar.append(Production(primary, [LeftBracket(), expression, RightBracket()]))
