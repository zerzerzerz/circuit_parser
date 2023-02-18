"""
Construct a mapping from each pin to integer.
Pins are extracted from cells and PI/PO
"""
from config import CELL_PIN_SEP, CONNECTION_SEP


def get_pin2index(at_rat_slew, net_delay:dict=None, cell_delay:dict=None, pipos:dict=None):
    '''
    Index dict for pin.
    Given a pin, get its index.
    pin is like '_347_{CELL_PIN_SEP}A1', where '_347_' is the instance name of cell, 'A1' is the pin.
    '''
    print(f"Constructing mapping between cell{CELL_PIN_SEP}pin to index")
    pins = set()

    if isinstance(at_rat_slew, dict):
        for pin in at_rat_slew.keys():
            pins.add(pin)
    
    if isinstance(net_delay, dict):
        for pin_pin in net_delay.keys():
            p1, p2 = pin_pin.split(CONNECTION_SEP)
            pins.add(p1)
            pins.add(p2)
    
    if isinstance(cell_delay, dict):
        for pin_pin in net_delay.keys():
            p1, p2 = pin_pin.split(CONNECTION_SEP)
            pins.add(p1)
            pins.add(p2)
    
    if isinstance(pipos, dict) and isinstance(pipos.get("PI"), list) and isinstance(pipos.get("PO"), list):
        pins.union(set(pipos["PI"]))
        pins.union(set(pipos["PO"]))
    
    pin2index = {}
    for i,pin in enumerate(sorted(list(pins))):
        pin2index[pin] = i

    return pin2index
    

