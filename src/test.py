import ast

# Create the AST for `x = 3 + 1`
assign_node = ast.Assign(
    targets=[ast.Name(id='x', ctx=ast.Store())],
    value=ast.BinOp(left=ast.Constant(value=3), op=ast.Add(), right=ast.Constant(value=1))
)

# Create the AST for `print(x)`
print_node = ast.Expr(
    value=ast.Call(
        func=ast.Name(id='print', ctx=ast.Load()),
        args=[ast.Name(id='x', ctx=ast.Load())],
        keywords=[]
    )
)

# Create a module node containing both statements
module_node = ast.Module(body=[assign_node, print_node], type_ignores=[])
# Automatically fix missing locations
ast.fix_missing_locations(module_node)
# Generate code from the AST
generated_code = ast.unparse(module_node)

print(generated_code)

