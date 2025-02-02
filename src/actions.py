from ast import AST, USub
import ast
from queue import LifoQueue
from symbol import Action
from tokens import Token
from typing import Literal
import logging

logger = logging.getLogger(__name__)


class StoreToBody(Action):
    """Action for appending values to a parent node's body attribute in the AST.

    Used to add statements or definitions to container nodes like modules,
    function bodies, or class bodies. Modifies the parent node in-place by
    appending the child value to its `body` attribute.
    """

    def call(self, ValueStack: LifoQueue, TokenStack: LifoQueue[Token]):
        """Modify parent node by appending child value to its body.

        :param ValueStack: LIFO queue containing AST nodes in order:

            - Top: Value to append (function, class, statement)
            - Next: Parent node with body attribute (module, function, etc)

        :param TokenStack: Not used in this action (interface consistency)

        Note: Parent node must have a `body` attribute (like :class:`ast.Module`)
        """
        value = ValueStack.get()
        print("value", value)
        module = ValueStack.get()
        print("module", module)

        module.body.append(value)
        ValueStack.put(module)


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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
        """Process the literal token and push converted value to ValueStack.

        :param ValueStack: LIFO queue holding AST nodes during parsing
        :param TokenStack: LIFO queue containing lexed tokens
        :raises ValueError: If conversion from lexeme to specified type fails
        """
        literal = TokenStack.get()

        try:
            converted_value = self.type(literal.lexeme)
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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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
                f"Unsupported operator {op_type.__name__}. " f"Allowed types: {allowed}"
            )

        self.op = op
        self.op_name = self.OP_NAMES[op_type]

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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
    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
        """Construct and push an If node to the value stack.

        :param ValueStack: LIFO queue containing:

            - Top: Body statements (typically a list of AST nodes)
            - Next: Test condition expression (AST node)

        :param TokenStack: Not used in this action (interface consistency)

        """
        body = ValueStack.get()
        expr = ValueStack.get()
        print("body", body, "expr", expr)

        node = ast.If(test=expr, body=[body], orelse=[])
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

    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue[Token]):
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
        else_body = ValueStack.get()
        if_node_or_expr = ValueStack.get()

        if isinstance(if_node_or_expr, ast.If):
            if_node = if_node_or_expr
            # Traverse to deepest orelse
            current = if_node
            while current.orelse and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]

            current.orelse = [else_body]
        else:
            expr = if_node_or_expr
            if_node = ValueStack.get()

            current = if_node
            while current.orelse and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]

            current.orelse = [ast.If(test=expr, body=[else_body])]
        ValueStack.put(if_node)


class HandleAllLoops(Action):
    def call(self, ValueStack, TokenStack):
        body = ValueStack.get()
        loop_data = ValueStack.get()

        if loop_data["type"] == "range":
            # Construct while loop with initializer and increment
            node = ast.While(
                test=loop_data["test"],
                body=[body] + [loop_data["increment"]],
                orelse=[],
            )

        else:  # while-style
            node = [
                loop_data["init"],
                ast.While(
                    test=loop_data["test"],
                    body=[body] + [loop_data["step"]],
                    orelse=[],
                ),
            ]
        ValueStack.put(loop_data["start"])
        StoreToBody().call(ValueStack, TokenStack)
        ValueStack.put(node)


class CreateRangeCondition(Action):
    """Handles both start:end and start:step:end ranges"""

    def call(self, ValueStack, TokenStack):
        end = ValueStack.get()
        assign_node = ValueStack.get()

        target = assign_node.targets[0]
        start = assign_node
        step = ast.Constant(value=1)
        
        test = ast.Compare(
            left=ast.Name(id=target.id, ctx=ast.Load()),
            ops=[
                ast.LtE()
            ],
            comparators=[end],
        )

        # Create increment operation
        increment = ast.AugAssign(target=target, op=ast.Add(), value=step)

        # Store components for loop construction
        ValueStack.put(
            {
                "type": "range",
                "target": target,
                "start": start,
                "end": end,
                "step": step,
                "test": test,
                "increment": increment,
            }
        )

class ExtendRangeCondition(Action):
    def call(self, ValueStack, TokenStack):
        end = ValueStack.get()
        loop_data = ValueStack.get()

        step = loop_data["end"]
        loop_data["step"] = step
        loop_data["end"] = end

        loop_data["test"].ops=[
                ast.LtE()
                if isinstance(step, ast.Constant) and step.value > 0
                else ast.GtE()
            ]
        loop_data["test"].comparators=[end]
        loop_data["increment"] = ast.AugAssign(target=loop_data["target"], op=ast.Add(), value=step)

        ValueStack.put(loop_data)


class CreateWhileCondition(Action):
    """Handles three-argument for loops (0;x<10;0)"""

    def call(self, ValueStack, TokenStack):
        step = ValueStack.get()
        test = ValueStack.get()
        init = ValueStack.get()
        target = ValueStack.get()

        return {"init": init, "test": test, "step": step}

class Break(Action):
    def call(self, ValueStack: LifoQueue[AST], TokenStack: LifoQueue):
        node = ast.Break()

        ValueStack.put(node)

class Print(Action):
    def call(self, ValueStack, TokenStack):
        value = ValueStack.get()

        node = ast.Expr(value=ast.Call(func=ast.Name(id="print", ctx=ast.Load()), args=[value]))

        ValueStack.put(node)

