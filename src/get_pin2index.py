"""
Construct a mapping from each pin to integer.
Pins are extracted from cells and PI/PO
"""
from config.config import CELL_PIN_SEP


def get_pin2index(cells, pipos):
    '''
    Index dict for pin.
    Given a pin, get its index.
    pin is like '_347_{CELL_PIN_SEP}A1', where '_347_' is the instance name of cell, 'A1' is the pin.
    '''
    print(f"Constructing mapping between cell{CELL_PIN_SEP}pin to index")
    pins = []
    pins.extend(pipos['PI'])
    pins.extend(pipos['PO'])

    for cell_name, cell in cells.items():
        for pin in cell['pins']:
            pin_name = f"{cell_name}{CELL_PIN_SEP}{pin['pin_name']}"
            pins.append(pin_name)
    pin2index = {k:v for v,k in enumerate(pins)}
    return pin2index
