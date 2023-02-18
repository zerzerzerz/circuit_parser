"""
Construct a mapping from each pin to integer.
Pins are extracted from cells and PI/PO
"""
from config import CELL_PIN_SEP, CONNECTION_SEP


def get_pin2index(net_delay:dict, cell_delay:dict):
    '''
    Index dict for pin.
    Given a pin, get its index.
    pin is like '_347_{CELL_PIN_SEP}A1', where '_347_' is the instance name of cell, 'A1' is the pin.
    '''
    print(f"Constructing mapping from cell{CELL_PIN_SEP}pin to index")
    pins = set()

    if isinstance(net_delay, dict):
        for pin_pin in net_delay.keys():
            p1, p2 = pin_pin.split(CONNECTION_SEP)
            pins.add(p1)
            pins.add(p2)
    
    if isinstance(cell_delay, dict):
        for pin_pin in cell_delay.keys():
            p1, p2 = pin_pin.split(CONNECTION_SEP)
            pins.add(p1)
            pins.add(p2)

    pin2index = {}
    for i,pin in enumerate(sorted(list(pins))):
        pin2index[pin] = i

    return pin2index
    

