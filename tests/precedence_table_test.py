import pytest
import pandas as pd
from precedence_table import precedence_table

def test_precedence_init():
    print(precedence_table)
    precedence_table.to_excel("~/output.xlsx")
    assert False
