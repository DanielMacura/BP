from typing import List


class Record:
    def __init__(self, name: str, body, selected: bool = True) -> None:
        self.record_type = name
        self.name = name
        self.body = body
        self.selected = selected


class Selector:
    """
    Holds information about all symbols i.e. all objects in the fdtd simulation. The simulation is an object, so are all the blocks and light sources.
    Also stores information about the selected symbols.
    """

    def __init__(self) -> None:
        self.records: List[Record] = []

    def getSelected(self) -> List[Record]:
        return [record for record in self.records if record.selected]

    def unselectAll(self) -> None:
        for record in self.records:
            record.selected = False

    def selectAll(self) -> None:
        for record in self.records:
            record.selected = True

    def add(self, record: Record) -> None:
        self.unselectAll()
        self.records.append(record)

    def setName(self, name: str) -> None:
        for record in self.records:
            if record.selected:
                record.name = name
