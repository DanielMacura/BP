import pandas as pd
from tokens import *
from enum import Enum

class Action(Enum):
    SHIFT_EQ = "shift_eq"  # For `=`
    SHIFT_LT = "shift_lt"  # For `<`
    REDUCE = "reduce"  # For `>`
    ERROR = "error"  # For blank
    END = "success"  # For end of parsing

precedence_table = {}

symbols = [
    Identifier, Plus, Minus, Multiply, Divide, Equal, LT, GT, GTE, LTE, LeftBracket, RightBracket
]

precedence_table = pd.DataFrame(
    Action.ERROR,
    index=symbols,
    columns=symbols
)

# Fill in specific values
precedence_table.loc['Equal', 'Plus'] = Action.SHIFT_EQ
precedence_table.loc['Plus', 'Multiply'] = Action.SHIFT_LT
precedence_table.loc['Multiply', 'Plus'] = Action.REDUCE

# Access specific actions
print(precedence_table.loc['Plus', 'Multiply'])  # Output: Action.SHIFT_LT
