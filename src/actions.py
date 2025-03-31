from ast import AST, USub
import ast
from queue import LifoQueue
from symbol import Action
from symtable import SymbolTable
from tokens import Token
from typing import Literal, Tuple, List
import logging

logger = logging.getLogger(__name__)


class StoreToBody(Action):
    """Action for appending values to a parent node's body attribute in the AST.

    Used to add statements or definitions to container nodes like modules,
    function bodies, or class bodies. Modifies the parent node in-place by
    appending the child value to its `body` attribute.
    """

    def call(
        self,
        ValueStack: LifoQueue,
        TokenStack: LifoQueue[Token],
    ):
        """Modify parent node by appending child value to its body.

        :param ValueStack: LIFO queue containing AST nodes in order:

            - Top: Value to append (function, class, statement)
            - Next: Parent node with body attribute (module, function, etc)

        :param TokenStack: Not used in this action (interface consistency)

        Note: Parent node must have a `body` attribute (like :class:`ast.Module`)
        """
        value = ValueStack.get()
        module = ValueStack.get()

        module.body.append(value)
        ValueStack.put(module)


class StoreToElse(Action):
    """Action for properly nesting else/elif bodies in AST If node chains.

    Handles two scenarios:
    1. Direct else attachment to existing If node
    2. Implicit elif creation from else-if patterns

    Stack Expectations:
    - Scenario 1 (Standard else):
        Top: Else body (list of statements)
        Next: ast.If node

    - Scenario 2 (Implicit elif):
        Top: Else body (list of statements)
        Next: Condition expression
        Next: Parent ast.If node

    :raises ValueError: If stack contents don't match expected patterns
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Process else clause body and modify AST structure accordingly.

        :param ValueStack: LIFO queue containing:
            - Top: Else clause body statements
            - Next: Either:
                a) ast.If node (direct else attachment), or
                b) condition expression followed by ast.If node (elif pattern)
        :param TokenStack: Not used in this action (interface consistency)

        Modifies the AST by:
        1. Finding the deepest nested orelse chain
        2. Appending else body to final node in chain
        3. Handling implicit elif conversion when needed

        Example transformations:
        Original if-elif-else structure:
            if(a) {} else if(b) {} else {}
        AST Result:
            If(
                test=a,
                body=[],
                orelse=[
                    If(
                        test=b,
                        body=[],
                        orelse=[]
                    )
                ]
            )
        """
        value = ValueStack.get()
        if_node_or_expr = ValueStack.get()

        if isinstance(if_node_or_expr, ast.If):
            if_node = if_node_or_expr
            current = if_node
            while current.orelse and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]

            current.orelse.append(value)
            ValueStack.put(if_node)
        else:
            if_node = ValueStack.get()
            expr = if_node_or_expr

            current = if_node
            while current.orelse and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            current.body.append(value)
            ValueStack.put(if_node)
            ValueStack.put(expr)


class StoreLiteral(Action):
    """Action for storing literals with type conversion to AST Constant nodes.

    Converts the token's lexeme value to the specified type and creates
    an :class:`ast.Constant` node for the abstract syntax tree.

    :param type: The target type for literal conversion. Must be one of
        ("str", "int", "float")
    :type type: Literal["str", "int", "float"]
    """

    def __init__(self, type: Literal["str", "int", "float"]):
        """Initialize literal storage with type conversion.

        :param type: String representing the target type. Valid values are
            "str" (string), "int" (integer), and "float" (floating-point).
        """
        self.type_map = {"int": int, "float": float, "str": str}
        self.type = self.type_map[type]

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Process the literal token and push converted value to ValueStack.

        :param ValueStack: LIFO queue holding AST nodes during parsing
        :param TokenStack: LIFO queue containing lexed tokens
        :raises ValueError: If conversion from lexeme to specified type fails
        """
        literal = TokenStack.get()

        try:
            converted_value = self.type(literal.lexeme)
            if self.type == str:
                converted_value = converted_value.strip('"')
        except ValueError as e:
            logger.error(
                f"Type conversion failed for '{literal.lexeme}' → "
                f"{self.type.__name__}: {str(e)}"
            )
            raise

        node = ast.Constant(value=converted_value)
        logger.info(f"Storing {self.type.__name__} literal: {converted_value}")
        ValueStack.put(node)


class AssignToVariable(Action):
    """Action for creating variable assignment nodes in the AST.

    Constructs an :class:`ast.Assign` node by combining a variable name
    and a value from the ValueStack. The assignment follows Python's
    target-value structure where ``name = value``.
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Create and push an assignment node to the ValueStack.

        :param ValueStack: LIFO queue containing AST elements in reverse order:

            - Top: Value to be assigned
            - Next: Target Name node for storage

        :param TokenStack: Not used in this action (maintained for interface consistency)
        :returns: None (pushes assignment node to ValueStack)
        """
        value = ValueStack.get()
        name = ValueStack.get()
        print(value, name)

        node = ast.Assign(targets=[name], value=value)
        ValueStack.put(node)


class StoreVariableName(Action):
    """Action for creating variable name nodes in assignment contexts.

    Generates an :class:`ast.Name` node with :class:`ast.Store` context
    for use in assignment targets. Captures variable names from the token stream.
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Process variable name token and create storage-context Name node.

        :param ValueStack: LIFO queue where the created Name node will be pushed
        :param TokenStack: LIFO queue containing identifier tokens
        :returns: None (pushes Name node to ValueStack)
        """
        name = TokenStack.get()

        node = ast.Name(id=name.lexeme, ctx=ast.Store())
        logger.info(f"Storing variable name {name.lexeme}")
        ValueStack.put(node)


class BinaryOperation(Action):
    """Action for performing binary operations in the abstract syntax tree.

    Handles all binary operations (addition, subtraction, etc.) by creating
    :class:`ast.BinOp` nodes. The specific operation is determined by the
    operator passed during initialization.

    :param op: The AST operator node to use for the binary operation.
        Must be one of: :class:`ast.Add`, :class:`ast.Sub`,
        :class:`ast.Mult`, or :class:`ast.Div`
    :type op: :class:`ast.operator`
    """

    OP_NAMES = {
        ast.Add: "addition",
        ast.Sub: "subtraction",
        ast.Mult: "multiplication",
        ast.Div: "division",
    }

    def __init__(self, op: ast.operator):
        """Initialize binary operation with specific operator.

        :raises ValueError: If unsupported operator type is provided
        """
        op_type = type(op)
        if op_type not in self.OP_NAMES:
            allowed = ", ".join(t.__name__ for t in self.OP_NAMES)
            raise ValueError(
                f"Unsupported operator {op_type.__name__}. Allowed types: {allowed}"
            )

        self.op = op
        self.op_name = self.OP_NAMES[op_type]

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Create and push binary operation node to ValueStack.

        :param ValueStack: LIFO queue containing AST nodes in reverse order:

            - Top: Right operand
            - Next: Left operand

        :param TokenStack: Not used in this action (maintained for interface consistency)
        """
        right = ValueStack.get()
        left = ValueStack.get()
        print(right, left)

        node = ast.BinOp(left=left, op=self.op, right=right)
        logger.info(f"Performing {self.op_name} on {left} and {right}")
        ValueStack.put(node)


class UnarySubtract(Action):
    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        operand = ValueStack.get()
        print(operand)

        node = ast.UnaryOp(op=USub(), operand=operand)
        logger.info(f"Unary subract {operand}")
        ValueStack.put(node)


class Comparison(Action):
    """Action for handling comparison operations and chained comparisons in AST.

    Constructs :class:`ast.Compare` nodes, either creating new comparisons or
    extending existing ones. Supports all Python comparison operators.

    :param op: The AST comparison operator node (e.g. :class:`ast.Eq`, :class:`ast.GtE`)
    :type op: :class:`ast.cmpop`

    Example usage::

        # Equality comparison
        eq_action = Comparison(ast.Eq())
        # Greater-than-or-equal comparison
        gte_action = Comparison(ast.GtE())
    """

    OP_SYMBOLS = {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Lt: "<",
        ast.LtE: "<=",
    }

    def __init__(self, op: ast.cmpop):
        """Initialize comparison action with specific operator.

        :raises TypeError: If provided operator isn't a valid comparison type
        """
        op_type = type(op)
        if op_type not in self.OP_SYMBOLS:
            allowed = ", ".join(t.__name__ for t in self.OP_SYMBOLS)
            raise TypeError(
                f"Invalid comparison operator {op_type.__name__}. "
                f"Must be one of: {allowed}"
            )

        self.op = op
        self.symbol = self.OP_SYMBOLS[op_type]

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Create or extend comparison node in the AST.

        :param ValueStack: LIFO queue containing AST nodes in order:

            - Top: Right operand
            - Next: Left operand (might be existing :class:`ast.Compare`)

        :param TokenStack: Not used (interface consistency)

        Chaining logic:

        - If left operand is existing comparison, extends its operators/comparators
        - Otherwise creates new comparison node

        Example chain::

            # For "a < b <= c"
            # First creates Compare(a < b)
            # Then extends with <= c
        """
        right = ValueStack.get()
        left = ValueStack.get()
        print("left", left, "right", right)

        if isinstance(left, ast.Compare):
            # Extend existing comparison chain
            node = ast.Compare(
                left=left.left,
                ops=left.ops + [self.op],
                comparators=left.comparators + [right],
            )
        else:
            # Create new comparison
            node = ast.Compare(left=left, ops=[self.op], comparators=[right])

        logger.info(f"Comparison: {left} {self.symbol} {right}")
        ValueStack.put(node)


class If(Action):
    """Action for constructing If nodes in the abstract syntax tree.

    Creates an :class:`ast.If` node by combining a test expression and body
    from the parser's value stack. Initializes the orelse (else clause)
    as an empty list for potential later extension by elif/else handling.

    Stack Expectations:

    - Top: Body of the if statement (list of AST nodes)
    - Next: Test expression (AST node)

    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """Construct and push an If node to the value stack.

        :param ValueStack: LIFO queue containing:

            - Top: Body statements (typically a list of AST nodes)
            - Next: Test condition expression (AST node)

        :param TokenStack: Not used in this action (interface consistency)

        """
        # body = ValueStack.get()
        expr = ValueStack.get()
        # print("body", body, "expr", expr)

        node = ast.If(test=expr, body=[], orelse=[])
        ValueStack.put(node)


class HandleElse(Action):
    """
    Action for attaching else clauses to the appropriate level in nested if/elif structures.

    Handles two scenarios:

    1. Direct else attachment to existing if node
    2. Implicit elif conversion when else follows a condition without body

    Stack Expectations:

    - Case 1 (Standard else):

        Top: else_body (list of statements)
        Next: ast.If node

    - Case 2 (Implicit elif):

        Top: else_body (list of statements)
        Next: condition expression
        Next: Parent ast.If node

    :raises ValueError: If stack contents don't match expected patterns
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue[Token],
    ):
        """
        Process else clause and modify AST structure accordingly.

        :param ValueStack: LIFO queue containing:
            - Top: Else clause body statements
            - Next: Either:

                a) ast.If node (direct else attachment), or
                b) condition expression followed by ast.If node (implicit elif)

        :param TokenStack: Not used in this action

        Modifies the AST by:

        1. Finding the deepest nested orelse chain
        2. Attaching else body to final if in chain
        3. Handling implicit elif conversion when needed

        """
        # else_body = ValueStack.get()
        if_node_or_expr = ValueStack.get()

        if isinstance(if_node_or_expr, ast.If):
            if_node = if_node_or_expr
            ValueStack.put(if_node)
        else:
            expr = if_node_or_expr
            if_node = ValueStack.get()

            current = if_node
            while current.orelse and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]

            current.orelse = [ast.If(test=expr, body=[])]
            ValueStack.put(if_node)
            ValueStack.put(expr)

        # if isinstance(if_node_or_expr, ast.If):
        #     if_node = if_node_or_expr
        #     # Traverse to deepest orelse
        #     current = if_node
        #     while current.orelse and isinstance(current.orelse[0], ast.If):
        #         current = current.orelse[0]
        #
        #     current.orelse = [else_body]
        # else:
        #     expr = if_node_or_expr
        #     if_node = ValueStack.get()
        #
        #     current = if_node
        #     while current.orelse and isinstance(current.orelse[0], ast.If):
        #         current = current.orelse[0]
        #
        #     current.orelse = [ast.If(test=expr, body=[else_body])]
        # ValueStack.put(if_node)


class CleanUpElse(Action):
    """Action for normalizing the stack state after else/elif clause processing.

    Ensures the final If node is properly positioned on the value stack by
    handling two possible stack configurations:
    1. Direct If node presence
    2. If node preceded by a conditional expression (elif pattern)

    Typical usage::

        # After processing else/elif bodies
        Production(
            else_clause,
            [
                Else(),
                condition,
                body,
                actions.CleanUpElse()
            ]
        )
    """

    def call(self, ValueStack, TokenStack):
        """Normalizes stack state by ensuring proper If node placement.

        :param ValueStack: LIFO queue containing either:
            - Top: ast.If node (direct case), or
            - Top: Conditional expression
              Next: ast.If node (elif pattern case)
        :param TokenStack: Not used in this action (interface consistency)

        Processing logic:
        1. Pops the top value which could be:
           - Direct If node, or
           - Conditional expression (with If node beneath it)
        2. Validates stack contents
        3. Ensures only the If node remains on the stack

        Modifies the ValueStack by:
        - Removing any temporary conditional expressions
        - Leaving the final If node properly positioned
        """
        if_node_or_expr = ValueStack.get()

        if isinstance(if_node_or_expr, ast.If):
            if_node = if_node_or_expr
        else:
            expr = if_node_or_expr
            if_node = ValueStack.get()

        ValueStack.put(if_node)


class CreateEmptyWhile(Action):
    """Action for initializing a While loop structure in the AST.

    Creates a placeholder :class:`ast.While` node with empty body and no test condition,
    allowing subsequent parsing actions to populate these components incrementally.

    Typical usage in grammar productions::

        Production(
            while_loop,
            [
                While(),
                actions.CreateEmptyWhile(),
                LeftBracket(),
                expression,  # Condition will be added later
                RightBracket(),
                LeftCurly(),
                body_statements,
                RightCurly()
            ]
        )

    Node Structure:
        Creates node with:
        - test: None (to be populated later)
        - body: Empty list (to be extended during parsing)
        - orelse: Empty list (no else clause by default)
    """

    def call(self, ValueStack, TokenStack):
        """Creates and pushes an empty While node to the value stack.

        :param ValueStack: LIFO queue where the new While node will be pushed
        :param TokenStack: Not used in this action (interface consistency)

        Processing flow:
        1. Creates barebones While node with:
           - test=None (temporary placeholder)
           - body=[]
        2. Pushes node to ValueStack for subsequent modifications
        3. Relies on later actions to:
           - Set test condition
           - Populate body contents
           - Handle else clauses if present

        ..note: The parser must ensure test condition is set before finalizing
        the loop structure to avoid invalid AST nodes.
        """
        node = ast.While(test=None, body=[])

        ValueStack.put(node)


class HandleAllLoops(Action):
    """Action for finalizing loop structures by assembling components into valid AST nodes.

    Handles both range-style and while-style loops by:
    1. Storing initial assignment before the loop
    2. Creating the While node body with increment step
    3. Maintaining proper parent body structure

    Stack Expectations:
    - Top: while_node (ast.While placeholder)
    - Next: increment_node (assignment step)
    - Next: start_node (initial assignment)

    Modified Stack After Processing:
    - Parent body contains:
        1. Initial assignment
        2. While loop
        3. Increment step (if applicable)
    """

    def call(self, ValueStack, TokenStack):
        """Assembles loop components into parent body structure.

        :param ValueStack: LIFO queue containing:
            - Top: Unconfigured While node
            - Next: Increment assignment node
            - Next: Initial assignment node
        :param TokenStack: Not used directly (forwarded to StoreToBody)
        :param SymbolTable: (Contextual) Current symbol table reference

        Processing Flow:
        1. Retrieve loop components from stack in reverse order:
           - while_node -> increment_node -> start_node
        2. Store initial assignment in parent body
        3. Store While node in parent body
        4. Store increment step after While node

        Example Transformation:
        Original Components:
            start_node: x = 1
            while_node: while(x <= 10)
            increment_node: x = x + 1

        Resulting Parent Body:
            [
                Assign(target=x, value=1),
                While(test=x <= 10, body=[...]),
                AugAssign(target=x, op=Add, value=1)
            ]
        """
        # body = ValueStack.get()
        # loop_data = ValueStack.get()

        while_node = ValueStack.get()
        increment_node = ValueStack.get()
        start_node = ValueStack.get()

        # if loop_data["type"] == "range":
        #     # Construct while loop with initializer and increment
        #     node = ast.While(
        #         test=loop_data["test"],
        #         body=[body] + [loop_data["increment"]],
        #         orelse=[],
        #     )

        # else:  # while-style
        #     node = [
        #         loop_data["init"],
        #         ast.While(
        #             test=loop_data["test"],
        #             body=[body] + [loop_data["step"]],
        #             orelse=[],
        #         ),
        #     ]

        # First push the starting variable value above the While loop
        # ValueStack.put(loop_data["start"])
        ValueStack.put(start_node)
        StoreToBody().call(ValueStack, TokenStack, SymbolTable)
        ValueStack.put(while_node)
        ValueStack.put(increment_node)
        StoreToBody().call(ValueStack, TokenStack, SymbolTable)


class CreateRangeCondition(Action):
    """Action for configuring range-based loop conditions in AST.

    Transforms Lumerical-style range syntax (start:end or start:step:end)
    into Python-compatible While loop structures with:
    - Initial assignment
    - Loop test condition
    - Increment operation

    Integrates with:
    - StoreToBody for parent structure management
    - HandleAllLoops for final assembly

    Handled Patterns:
    - for(x=1:10) → while x <= 10 with x += 1
    - for(x=1:2:10) → while x <= 10 with x += 2
    """

    def call(self, ValueStack, TokenStack):
        """Process range components and configure While loop node.

        :param ValueStack: LIFO queue containing:
            - Top: End value (AST node)
            - Next: Initial assignment node (ast.Assign)
            - Next: Unconfigured While node (ast.While)
        :param TokenStack: Not used directly (interface consistency)

        Processing Flow:
        1. Extract end boundary from stack
        2. Retrieve initial assignment (e.g., x=1)
        3. Configure While node with test condition
        4. Generate increment operation
        5. Re-stack components for final assembly

        Modifies Stack To:
            - Top: Configured While node
            - Next: Increment operation
            - Next: Initial assignment

        Example Transformation:
            Input Stack:
                Constant(value=10)
                Assign(target=x, value=1)
                While(test=None, body=[])

            Output Stack:
                While(test=x <= 10, body=[])
                AugAssign(target=x, op=Add, value=1)
                Assign(target=x, value=1)
        """
        end = ValueStack.get()
        assign_node = ValueStack.get()
        while_node: ast.While = ValueStack.get()

        target = assign_node.targets[0]
        start = assign_node
        step = ast.Constant(value=1)

        test = ast.Compare(
            left=ast.Name(id=target.id, ctx=ast.Load()),
            ops=[ast.LtE()],
            comparators=[end],
        )

        # Create increment operation
        increment_node = ast.AugAssign(target=target, op=ast.Add(), value=step)

        while_node.test = test
        ValueStack.put(assign_node)
        ValueStack.put(increment_node)
        ValueStack.put(while_node)


class ExtendRangeCondition(Action):
    """Action for extending range-based loop conditions with step values.

    Handles the second colon in range syntax (start:step:end) by:
    1. Updating the loop's termination condition
    2. Adjusting the increment operation
    3. Modifying comparison operators based on step direction

    Stack Expectations:
    - Top: End value (AST node)
    - Next: Partially configured While node
    - Next: Increment operation node (AugAssign)
    """

    def call(self, ValueStack, TokenStack):
        """Process step value and finalize range condition configuration.

        :param ValueStack: LIFO queue containing:
            - Top: Final end value for range
            - Next: While node with initial test
            - Next: Increment node with step value
        :param TokenStack: Not used directly (interface consistency)

        Processing Flow:
        1. Retrieves final end value from stack
        2. Updates While node's test comparator
        3. Adjusts comparison operator based on step sign
        4. Reassembles components for final processing

        Modifies:
        - While node's test.comparators
        - While node's test.ops (conditionally)
        - Increment node's value

        Example Transformation:
        Initial Configuration:
            While(test=x <= 10, ...)
            AugAssign(value=2)
            New end: 20

        Result:
            While(test=x <= 20, ...)
            AugAssign(value=2)
        """
        end = ValueStack.get()
        # loop_data = ValueStack.get()
        while_node: ast.While = ValueStack.get()
        increment_node: ast.AugAssign = ValueStack.get()

        increment_node.value = while_node.test.comparators[0]

        # step = loop_data["end"]
        # loop_data["step"] = step
        # loop_data["end"] = end

        while_node.test.comparators = [end]

        # TODO FIXME
        if isinstance(increment_node, ast.Constant) and increment_node.value > 0:
            while_node.test.ops = [ast.GtE()]
        # loop_data["test"].ops=[
        #         ast.LtE()
        #         if isinstance(step, ast.Constant) and step.value > 0
        #         else ast.GtE()
        #     ]

        # loop_data["test"].comparators=[end]
        # loop_data["increment"] = ast.AugAssign(target=loop_data["target"], op=ast.Add(), value=step)

        # ValueStack.put(loop_data)
        ValueStack.put(increment_node)
        ValueStack.put(while_node)


class CreateWhileCondition(Action):
    """Action for processing three-argument while-style loop components.

    Handles Lumerical's `for(init; test; step)` syntax used to implement while loops.
    Collects loop components into a structured dictionary for later processing.

    Stack Expectations:
    - Top: step (third argument, typically dummy value)
    - Next: test (loop condition expression)
    - Next: init (initial assignment, typically dummy value)
    - Next: target (loop variable reference)

    Output:
    Pushes dictionary with keys:
    - "init": Initial assignment node
    - "test": Condition check node
    - "step": Step operation node
    """

    def call(self, ValueStack, TokenStack):
        """Packages while-loop components into a structured dictionary.

        :param ValueStack: LIFO queue containing:
            - Top: step (AST node, typically constant 0)
            - Next: test (ast.Compare node)
            - Next: init (ast.Assign node)
            - Next: target (ast.Name node)
        :param TokenStack: Not used (interface consistency)

        Example Usage:
        For Lumerical code `for(0; x<10; 0) { ... }`
        Processes components to create:
            {
                "init": Assign(target=x, value=0),
                "test": Compare(x < 10),
                "step": Assign(target=x, value=0)
            }
        """
        step = ValueStack.get()
        test = ValueStack.get()
        init = ValueStack.get()
        target = ValueStack.get()

        return {"init": init, "test": test, "step": step}


class Break(Action):
    """Action for creating break statements in loop control flow.

    Generates an :class:`ast.Break` node to represent the `break` keyword
    in loop structures. This node will be added to the nearest enclosing
    loop's body during AST construction.

    Example usage in grammar::

        Production(
            jump_statement,
            [
                Break(),
                Semicolon()
            ]
        )
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue,
    ):
        """Creates and pushes a Break node to the value stack.

        :param ValueStack: LIFO queue where the Break node will be added
        :param TokenStack: Not used in this action (interface consistency)

        Processing flow:
        1. Creates bare Break node
        2. Pushes node to ValueStack for inclusion in parent body
        3. Relies on containing loop structure for context validity

        Example AST result:
            Break()

        Note: Does not validate proper loop context - parser must ensure
        break statements only appear inside loops.
        """
        node = ast.Break()

        ValueStack.put(node)


class Print(Action):
    """Action for creating print statement nodes in the AST.

    Translates Lumerical's `?` operator syntax into Python print calls.
    Constructs an :class:`ast.Expr` node containing a call to the print function.

    Example conversion:
        Lumerical: ?x;
        Python: print(x)
    """

    def call(self, ValueStack, TokenStack):
        """Creates and pushes a print call node to the value stack.

        :param ValueStack: LIFO queue containing:
            - Top: Value to be printed (AST node)
        :param TokenStack: Not used in this action (interface consistency)

        Processing Flow:
        1. Retrieves value to print from stack
        2. Constructs print call AST node
        3. Pushes node back to stack for parent body inclusion

        Resulting AST Structure:
            Expr(
                value=Call(
                    func=Name(id='print', ctx=Load()),
                    args=[<value>],
                    keywords=[]
                )
            )

        Note: Only supports single-argument print statements. For multiple
        arguments, additional handling would be required.
        """
        value = ValueStack.get()

        node = ast.Expr(
            value=ast.Call(func=ast.Name(id="print", ctx=ast.Load()), args=[value])
        )

        ValueStack.put(node)


class Imports(Action):
    """Action for injecting mandatory import statements into the AST.

    Generates hardcoded import declarations required for Lumerical script compatibility:
    1. `import meep as mp`
    2. `from runtime import Selector, Record`

    These imports are automatically added to the module body regardless of user code.
    """

    def call(
        self,
        ValueStack: LifoQueue[AST],
        TokenStack: LifoQueue,
    ):
        """Creates and stores import nodes in the AST body.

        :param ValueStack: LIFO queue used for AST construction
        :param TokenStack: Not used in this action (interface consistency)

        Processing Flow:
        1. Creates meep import node
        2. Stores it in parent body via StoreToBody
        3. Creates runtime selectors import node
        4. Leaves it on stack for subsequent processing

        Generated AST Nodes:
        - Import(alias(name='meep', asname='mp'))
        - ImportFrom(
            module='runtime',
            names=[alias(name='Selector'), alias(name='Record')],
            level=0
          )

        Note: These imports are added automatically, not based on user code.
        """
        import_meep = ast.Import(names=[ast.alias(name="meep", asname="mp")])

        import_selector = ast.ImportFrom(
            module="runtime",
            names=[
                ast.alias(name="Selector", asname=None),
                ast.alias(name="Record", asname=None),
            ],
            level=0,  # Absolute import
        )

        ValueStack.put(import_meep)
        StoreToBody().call(ValueStack, TokenStack)
        ValueStack.put(import_selector)


class CreateSelector(Action):
    """Action for creating a Selector instance assignment in the AST.

    Generates an assignment node that initializes a `selector` variable
    with a `Selector()` constructor call. This is typically used for
    Lumerical script compatibility where selector objects are required.

    Example AST Output:
        Assign(
            targets=[Name(id='selector', ctx=Store())],
            value=Call(
                func=Name(id='Selector', ctx=Load()),
                args=[],
                keywords=[]
            )
        )
    """

    def call(self, ValueStack, TokenStack: LifoQueue):
        """Creates and pushes a Selector initialization node to the value stack.

        :param ValueStack: LIFO queue where the assignment node will be placed
        :param TokenStack: Not used in this action (interface consistency)

        Node Details:
        - Creates a variable assignment: `selector = Selector()`
        - Uses empty constructor arguments
        - Assigns to fixed variable name 'selector'

        Integration Points:
        - Requires prior import of Selector via `Imports` action
        - Typically followed by `StoreToBody` to add to parent scope

        Note: This creates a fresh selector instance regardless of existing
        variables with the same name in the scope.
        """
        # Generate: selector = Selector()
        node = ast.Assign(
            targets=[ast.Name(id="selector", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="Selector", ctx=ast.Load()), args=[], keywords=[]
            ),
        )
        ValueStack.put(node)


class SetProperty(Action):
    """Action for generating property assignments on selector records.

    Handles three types of property assignments:
    1. Direct name assignments
    2. Geometric center coordinates (x/y/z)
    3. Size spans (x span/y span/z span)

    Requires prior initialization of:
    - `selector` variable via CreateSelector
    - `mp` module import (from meep)
    """

    def call(self, ValueStack, TokenStack: LifoQueue):
        """Creates AST nodes for property assignment loops.

        :param ValueStack: LIFO queue containing:
            - Top: Property value (AST node)
            - Next: Property name (ast.Constant)
        :param TokenStack: Not used directly (interface consistency)

        Processing Flow:
        1. Retrieves property name and value from stack
        2. Generates appropriate assignment loop based on property type
        3. Pushes resulting loop node to stack

        Match Cases:
        - "name": Direct name assignment to records
        - "x"/"y"/"z": Center coordinate assignment
        - "* span": Size dimension assignment

        Example Output for "x" assignment:
            For(
                target=Name(id='record'),
                iter=Call(
                    func=Attribute(
                        value=Name(id='selector'),
                        attr='getSelected'),
                body=[
                    Assign(
                        targets=[Attribute(
                            value=Name(id='record'),
                            attr='center')],
                        value=Call(
                            func=Attribute(
                                value=Name(id='mp'),
                                attr='Vector3'),
                            args=[<x_val>, <existing_y>, <existing_z>]
                        )
                    )
                ]
            )
        """
        value = ValueStack.get()
        name: ast.Constant = ValueStack.get()
        logger.debug(f"Processing property {name.value} with value {value}")

        # Common AST components
        selector_ref = ast.Name(id="selector", ctx=ast.Load())
        mp_vector3 = ast.Attribute(
            value=ast.Name(id="mp", ctx=ast.Load()), attr="Vector3", ctx=ast.Load()
        )

        def create_loop_body(attr: str, components: list) -> ast.stmt:
            """Create assignment body for vector properties"""
            return ast.Assign(
                targets=[
                    ast.Attribute(
                        value=ast.Name(id="record", ctx=ast.Load()),
                        attr=attr,
                        ctx=ast.Store(),
                    )
                ],
                value=ast.Call(func=mp_vector3, args=components, keywords=[]),
            )

        def create_getSelected_loop(body: List[ast.AST]) -> ast.For:
            return ast.For(
                target=ast.Name(id="record", ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Attribute(selector_ref, "getSelected", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                ),
                body=body,
                orelse=[],
            )

        match name.value:
            case "name":
                # Generate: for record in selector.getSelected(): record.name = value
                body = [
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                ast.Name(id="record", ctx=ast.Load()),
                                "name",
                                ctx=ast.Store(),
                            )
                        ],
                        value=value,
                    )
                ]
                loop = create_getSelected_loop(body)

                ValueStack.put(loop)

            case axis if axis in {"x", "y", "z"}:
                # Generate vector components while preserving others
                components = [
                    value
                    if a == axis
                    else ast.Attribute(
                        ast.Attribute(
                            ast.Name(id="record", ctx=ast.Load()),
                            "center",
                            ctx=ast.Load(),
                        ),
                        a,
                        ctx=ast.Load(),
                    )
                    for a in ["x", "y", "z"]
                ]
                loop_body = create_loop_body("center", components)
                loop = create_getSelected_loop([loop_body])
                ValueStack.put(loop)

            case span if span.endswith(" span"):
                axis = span.split()[0]
                components = [
                    value
                    if a == axis
                    else ast.Attribute(
                        ast.Attribute(
                            ast.Name(id="record", ctx=ast.Load()),
                            "size",
                            ctx=ast.Load(),
                        ),
                        a,
                        ctx=ast.Load(),
                    )
                    for a in ["x", "y", "z"]
                ]
                loop_body = create_loop_body("size", components)
                loop = create_getSelected_loop([loop_body])
                ValueStack.put(loop)

            case _:
                logger.warning(f"Unsupported property: {name.value}")
                ValueStack.put(ast.Pass())


def AddToSelector(args: Tuple[ast.Constant, ast.Call, ast.Constant]) -> ast.Expr:
    """Constructs AST nodes for adding a Record to a Selector.

    Generates an expression node representing the operation:
    `selector.add(Record(name, value, unit))`

    :param args: Tuple containing three elements:
        - [0]: Name of the record (ast.Constant)
        - [1]: Value of the record (ast.Call)
        - [2]: Unit specification (ast.Constant)
    :return: Expression node representing the add operation

    Example AST output:
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='selector'),
                    attr='add'
                ),
                args=[
                    Call(
                        func=Name(id='Record'),
                        args=[
                            Constant(value='material'),
                            Call(...),  # Value expression
                            Constant(value='unit')
                        ]
                    )
                ]
            )
        )

    Dependencies:
    - Requires `selector` variable initialized via CreateSelector
    - Requires `Record` imported from runtime module
    """
    return ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                ast.Name(id="selector", ctx=ast.Load()), "add", ctx=ast.Load()
            ),
            args=[
                ast.Call(
                    func=ast.Name(id="Record", ctx=ast.Load()),
                    args=args,
                    keywords=[],
                )
            ],
            keywords=[],
        )
    )


class AddRect(Action):
    """Action for creating and adding a rectangular block to the selector.

    Generates AST nodes to create a Meep rectangular block with default size
    and adds it to the selector using the Record pattern. This represents
    Lumerical's rectangle creation syntax with default placeholder values.

    Example generated code:
        selector.add(Record(
            "Rectangle",
            mp.Block(size=mp.Vector3(1,1,1)),
            True
        ))
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes rectangle Record addition to the value stack.

        :param ValueStack: LIFO queue where the expression will be pushed
        :param TokenStack: Not used in this action (interface consistency)

        Node Structure:
        - Creates a Record with:
            - Name: "Rectangle"
            - Value: mp.Block with default size (1,1,1)
            - Unit: True (boolean placeholder)

        Dependencies:
        - Requires `mp` (meep) module import
        - Requires `Record` and `selector` initialization

        Note: Currently uses hardcoded default values. For dynamic size/materials,
        additional processing would be needed.
        """
        ValueStack.put(
            AddToSelector(
                [
                    ast.Constant(value="Rectangle"),
                    ast.Call(
                        func=ast.Attribute(
                            ast.Name(id="mp", ctx=ast.Load()),
                            "Block",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg="size",
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="mp", ctx=ast.Load()),
                                        attr="Vector3",
                                        ctx=ast.Load(),
                                    ),
                                    args=[
                                        ast.Constant(value=1),
                                        ast.Constant(value=1),
                                        ast.Constant(value=1),
                                    ],
                                    keywords=[],
                                ),
                            )
                        ],
                    ),
                    ast.Constant(value=True),
                ]
            )
        )


class AddFDTD(Action):
    """Action for creating and adding a basic FDTD simulation region to the selector.

    Generates AST nodes to initialize a Meep simulation with default parameters
    and adds it to the selector using the Record pattern. This represents
    Lumerical's FDTD solution region setup with placeholder values.

    Example generated code:
        selector.add(Record(
            "Simulation",
            mp.Simulation(cell_size=mp.Vector3(1,1,1)),
            True
        ))
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes FDTD simulation Record addition to the value stack.

        :param ValueStack: LIFO queue where the expression will be pushed
        :param TokenStack: Not used in this action (interface consistency)

        Node Structure:
        - Creates a Record with:
            - Name: "Simulation"
            - Value: mp.Simulation with default 1x1x1 cell size
            - Unit: True (boolean placeholder)

        Dependencies:
        - Requires `mp` (meep) module import
        - Requires `Record` and `selector` initialization
        - Depends on Meep's Simulation and Vector3 classes

        Note: Current implementation uses hardcoded defaults for:
        - cell_size (mp.Vector3(1,1,1))
        - Other simulation parameters (not shown)
        Real-world usage would require extending with actual parameters.
        """
        ValueStack.put(
            AddToSelector(
                [
                    ast.Constant(value="Simulation"),  # Record name
                    ast.Call(  # Simulation object
                        func=ast.Attribute(
                            value=ast.Name(id="mp", ctx=ast.Load()),
                            attr="Simulation",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg="cell_size",
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id="mp", ctx=ast.Load()),
                                        attr="Vector3",
                                        ctx=ast.Load(),
                                    ),
                                    args=[
                                        ast.Constant(value=1),
                                        ast.Constant(value=1),
                                        ast.Constant(value=1),
                                    ],
                                    keywords=[],
                                ),
                            )
                        ],
                    ),
                    ast.Constant(value=True),  # selected
                ]
            )
        )


class SelectAll(Action):
    """Action for creating a 'select all records' operation in the AST.

    Generates an expression node that calls the `selectAll` method on the
    selector object, typically used to select all available records in
    Lumerical's scripting context.
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes a selectAll call node to the value stack.

        :param ValueStack: LIFO queue where the expression will be placed
        :param TokenStack: Not used in this action (interface consistency)

        Generated AST Node:
        ```python
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='selector', ctx=Load()),
                    attr='selectAll',
                    ctx=Load()
                ),
                args=[],
                keywords=[]
            )
        )
        ```

        Equivalent Python Code:
        ```python
        selector.selectAll()
        ```

        Dependencies:
        - Requires `selector` variable initialized via CreateSelector
        - Depends on Selector class from runtime imports
        - Assumes selector object has selectAll() method

        Note: This action doesn't return a value but modifies the selector's
        internal state. Typically used before bulk operations on records.
        """
        node = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="selector", ctx=ast.Load()),
                    attr="selectAll",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            )
        )
        ValueStack.put(node)


class UnselectAll(Action):
    """Action for creating an 'unselect all records' operation in the AST.

    Generates an expression node that calls the `unselectAll` method on the
    selector object, typically used to clear all record selections in
    Lumerical's scripting context.
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes an unselectAll call node to the value stack.

        :param ValueStack: LIFO queue where the expression will be placed
        :param TokenStack: Not used in this action (interface consistency)

        Generated AST Node:
        ```python
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='selector', ctx=Load()),
                    attr='unselectAll',
                    ctx=Load()
                ),
                args=[],
                keywords=[]
            )
        )
        ```

        Equivalent Python Code:
        ```python
        selector.unselectAll()
        ```

        Dependencies:
        - Requires `selector` variable initialized via CreateSelector
        - Depends on Selector class from runtime imports
        - Assumes selector object has unselectAll() method

        Note: This action clears the selector's current selection without
        returning a value. Typically used after bulk operations or before
        making new selections.
        """
        node = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="selector", ctx=ast.Load()),
                    attr="unselectAll",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            )
        )
        ValueStack.put(node)


class Select(Action):
    """Action for creating a 'select specific record' operation in the AST.

    Generates an expression node that calls the `select` method on the
    selector object to select a specific record by name.
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes a select call node to the value stack.

        :param ValueStack: LIFO queue containing:
            - Top: Name of record to select (ast.Constant)
        :param TokenStack: Not used in this action (interface consistency)

        Generated AST Node:
        ```python
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='selector', ctx=Load()),
                    attr='select',
                    ctx=Load()
                ),
                args=[<name_node>],
                keywords=[]
            )
        )
        ```

        Equivalent Python Code:
        ```python
        selector.select("material_silicon")
        ```

        Dependencies:
        - Requires `selector` variable initialized via CreateSelector
        - Assumes selector object has select() method
        - Name argument must be a string constant

        Note: Typically used for precise selection of individual records
        after initial bulk operations.
        """
        name = ValueStack.get()
        node = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="selector", ctx=ast.Load()),
                    attr="select",
                    ctx=ast.Load(),
                ),
                args=[name],
                keywords=[],
            )
        )
        ValueStack.put(node)


class ShiftSelect(Action):
    """Action for creating a 'shift-select' operation to add records to the current selection.

    Generates an expression node that calls the `shiftSelect` method on the selector object,
    typically used to add a specific record to an existing selection (similar to Ctrl/Cmd+click
    in GUI environments).
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue):
        """Creates and pushes a shiftSelect call node to the value stack.

        :param ValueStack: LIFO queue containing:
            - Top: Name of record to add to selection (ast.Constant)
        :param TokenStack: Not used in this action (interface consistency)

        Generated AST Node:
        ```python
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='selector', ctx=Load()),
                    attr='shiftSelect',
                    ctx=Load()
                ),
                args=[<name_node>],
                keywords=[]
            )
        )
        ```

        Equivalent Python Code:
        ```python
        selector.shiftSelect("waveguide_property")
        ```

        Dependencies:
        - Requires `selector` variable initialized via CreateSelector
        - Assumes selector object has shiftSelect() method
        - Requires prior selection to exist for meaningful operation

        Note: Used for cumulative selections rather than replacing the current selection.
        Typically combined with initial select() or selectAll() calls.
        """
        name = ValueStack.get()
        node = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="selector", ctx=ast.Load()),
                    attr="shiftSelect",
                    ctx=ast.Load(),
                ),
                args=[name],
                keywords=[],
            )
        )
        ValueStack.put(node)
