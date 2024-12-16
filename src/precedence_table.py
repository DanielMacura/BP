import pandas as pd
from tokens import Token
from tokens import (
    Identifier,
    Plus,
    Minus,
    Multiply,
    Divide,
    Equal,
    LT,
    GT,
    GTE,
    LTE,
    LeftBracket,
    RightBracket,
)
from enum import Enum


class Action(Enum):
    """Actions in the precedence table.

    :param SHIFT_EQ:
    :param SHIFT_LT:
    :param REDUCE:
    :param ERROR:
    :param END:
    """

    SHIFT_EQ = "shift_eq"  # For `=`
    SHIFT_LT = "shift_lt"  # For `<`
    REDUCE = "reduce"  # For `>`
    ERROR = "error"  # For blank
    END = "success"  # For end of parsing


class PrecedenceTable:
    """The :py:class:`PrecedenceTable` provides methods to interact with the precedence table.
    A precedence table is usually hand written and later loaded from a file for use in the parser.

    :param symbols: List of all symbols the precedence table accepts.
    :param symbol_names: Mappings of symbol class names, to be stored in the precedence file.
    :param table: The table has the same index and columns, a square shape.
    """

    symbols = [
        Identifier,
        Plus,
        Minus,
        Multiply,
        Divide,
        Equal,
        LT,
        GT,
        GTE,
        LTE,
        LeftBracket,
        RightBracket,
    ]
    symbol_names = {cls.__class__: cls for cls in symbols}

    def __init__(self) -> None:
        self.table = pd.DataFrame(
            Action.ERROR.value,
            index=self.symbol_names.keys(),
            columns=self.symbol_names.keys(),
        )

    def save(self, filepath: str) -> None:
        """Save the precedence table as a Excel spreadsheet for easy editing.

        :param filepath: File path where the precedence table will be stored.
        """
        self.table.to_excel(filepath)

    def load(self, filepath: str) -> None:
        """Load the precedence table from an Excel file.
        The shape is checked and so are the indexes.

        :param filepath: File path to load the precedence table from.
        :raises ValueError: If the shape is not a square.
        :raises ValueError: If the index is not unique.
        """
        self.table = pd.read_excel(filepath, index_col=0)

        if self.table.shape[0] != self.table.shape[1]:
            raise ValueError("The loaded precedence table is not a square shape.")
        if not self.table.index.is_unique:
            raise ValueError("The index is not unique.")

    def getPrecedence(self, top: None | Token, input: None | Token) -> Action:
        if top not in PrecedenceTable.symbols or input not in PrecedenceTable.symbols:
            raise ValueError("Got a token not present in the precedence table.")
        return self.table.loc[type(top), type(input)]
