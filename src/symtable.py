from itertools import count

object_incrementor = count(0, 1)


class Record:
    def __init__(self, record_type:str, name=None) -> None:
        self.record_type = record_type
        self.name = name if name else f"object_{object_incrementor.__next__()}"


class SymbolTable:
    """
    Holds information about all symbols i.e. all objects in the fdtd simulation. The simulation is an object, so are all the blocks and light sources.
    Also stores information about the selected symbols.
    """

    def __init__(self) -> None:
        self.selected = []
        self.symbols = []

    def add(self, record: Record) -> None:
        self.symbols.append(record)
        self.selected = [record]

    def setName(self, name: str) -> None:
        if self.selected == []:
            raise ValueError("Set name was called but there is no selected object.")

        self.selected[0].name = name
