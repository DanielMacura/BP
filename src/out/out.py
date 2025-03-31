import meep as mp
from runtime import Selector, Record
selector = Selector()
selector.add(Record('Simulation', mp.Simulation(mp.Vector3(1,1,1)), True))
selector.add(Record('Rectangle', mp.Block(mp.Vector3(1,1,1)), True))
selector.add(Record('Rectangle', mp.Block(mp.Vector3(1,1,1)), True))
for record in selector.getSelected():
    record.name = 'block'
for record in selector.getSelected():
    record.center = mp.Vector3(5, record.center.y, record.center.z)
for record in selector.getSelected():
    record.size = mp.Vector3(7, record.size.y, record.size.z)
selector.shiftSelect('Rectangle')
for record in selector.getSelected():
    record.size = mp.Vector3(record.size.x, record.size.y, 11)
selector.select('block')
for record in selector.getSelected():
    record.center = mp.Vector3(record.center.x, record.center.y, 2 + 2)
